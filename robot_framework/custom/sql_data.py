"""Functions for getting data from SQL for people who moved into the city of Aarhus."""
from datetime import date, timedelta

import pyodbc

CONNECTION_STRING = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=FaellesSQL;DATABASE=DWH;Trusted_Connection=yes"

# Flyttehistorik has one row per move, where DatoLastTilflytAAK is the date of the person's most
# recent move into Aarhus, and DatoFraflyt is the date they moved out of that particular address.
# DatoFraflyt is never NULL: an address they still live at gets the sentinel date 9999-12-31, so
# that plus Komkode = '0751' means they live here now.
# The table does not record where a move came *from*, so LAG is used to put the previous address of
# each move on its row, which is how we tell an arrival from abroad from a move within Denmark.
# AdresseAktuel is used to get the name and filter people who are dead, young or missing.
# Takes the earliest and latest arrival date to consider as parameters, in that order.
LETTER_RECEIVERS_QUERY = """
    -- Everyone whose latest arrival in Aarhus falls in the period we are sending letters for
    WITH candidates AS (
        SELECT
            AdresseAktuel.CPR,
            AdresseAktuel.Fornavn AS given_name,
            Flyttehistorik.DatoLastTilflytAAK AS arrival_date
        FROM DWH.Mart.AdresseAktuel
        JOIN DWH.dwh.Flyttehistorik ON AdresseAktuel.CPR = Flyttehistorik.CPR
        -- The address they have not moved out of, ie. where they live now
        WHERE Flyttehistorik.DatoFraflyt = '9999-12-31'
            AND Flyttehistorik.Komkode = '0751' -- Aarhus Kommune
            AND AdresseAktuel.Forsvundet = 0
            AND AdresseAktuel.Doedsdato IS NULL
            AND AdresseAktuel.Alder >= 18
            AND AdresseAktuel.HerkomstKode <> 'DK'
            AND Flyttehistorik.DatoLastTilflytAAK BETWEEN ? AND ?
    ),
    -- Where each of their moves came from. Restricted to candidates so the window functions run
    -- over a few thousand people's history instead of every move ever made in the country.
    moves AS (
        SELECT raw.CPR, raw.DatoTilflyt,
        LAG(raw.Komkode) OVER (PARTITION BY raw.CPR ORDER BY raw.DatoTilflyt) AS from_kom_kode,
        LAG(raw.Vejkode) OVER (PARTITION BY raw.CPR ORDER BY raw.DatoTilflyt) AS from_vej_kode
        FROM DWH.dwh.Flyttehistorik raw
        JOIN candidates ON candidates.CPR = raw.CPR
    )
    SELECT candidates.CPR, candidates.given_name, candidates.arrival_date
    FROM candidates
    -- The move that brought them here, so we can see where they came from
    JOIN moves ON moves.CPR = candidates.CPR AND moves.DatoTilflyt = candidates.arrival_date
    WHERE moves.from_kom_kode NOT IN ('0101' ,'0147' ,'0151' ,'0153' ,'0155' ,'0157' ,'0159' ,'0161' ,'0163' ,'0165' ,'0167' ,'0169' ,'0173' ,'0175' ,'0183' ,'0185' ,'0187' ,'0190' ,'0201' ,'0210' ,'0217' ,'0219' ,'0223' ,'0230' ,'0240' ,'0250' ,'0253' ,'0259' ,'0260' ,'0265' ,'0269' ,'0270' ,'0306' ,'0316' ,'0320' ,'0326' ,'0329' ,'0330' ,'0336' ,'0340' ,'0350' ,'0360' ,'0370' ,'0376' ,'0390' ,'0400' ,'0410' ,'0411' ,'0420' ,'0430' ,'0440' ,'0450' ,'0461' ,'0479' ,'0480' ,'0482' ,'0492' ,'0510' ,'0530' ,'0540' ,'0550' ,'0561' ,'0563' ,'0573' ,'0575' ,'0580' ,'0607' ,'0615' ,'0621' ,'0630' ,'0657' ,'0661' ,'0665' ,'0671' ,'0706' ,'0707' ,'0710' ,'0727' ,'0730' ,'0740' ,'0741' ,'0746' ,'0751' ,'0756' ,'0760' ,'0766' ,'0773' ,'0779' ,'0787' ,'0791' ,'0810' ,'0813' ,'0820' ,'0825' ,'0840' ,'0846' ,'0849' ,'0851' ,'0860') -- Danish commune codes, so anything else is outside Denmark
        AND moves.from_vej_kode NOT IN ('9902', '9901') -- Homeless and couch surfers
    """


def get_letter_receivers(min_days_since_arrival: int, max_days_since_arrival: int) -> list[pyodbc.Row]:
    """Get everyone whose welcome letter is due now.

    Args:
        min_days_since_arrival: How long to wait after a person arrived before their letter is due.
        max_days_since_arrival: How far back to look for arrivals, so we don't look through the entire move history.

    Returns:
        List of rows of cpr, first name and arrival date.
    """
    today = date.today()
    earliest_arrival = today - timedelta(days=max_days_since_arrival)
    latest_arrival = today - timedelta(days=min_days_since_arrival)

    connection = pyodbc.connect(CONNECTION_STRING)
    try:
        cursor = connection.cursor()
        cursor.execute(LETTER_RECEIVERS_QUERY, earliest_arrival, latest_arrival)
        return cursor.fetchall()
    finally:
        connection.close()
