"""Functions for getting data from SQL for people who moved into the city of Aarhus."""
from datetime import datetime, timedelta

import pyodbc

CONNECTION_STRING = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=FaellesSQL;DATABASE=DWH;Trusted_Connection=yes"

# Flyttehistorik is a log with one row per move, where Komkode is the commune the person moved *to*.
# LAG is used to also put the commune they moved *from* on each row, so every row describes a single
# move as a from/to pair. The move we are looking for is the most recent one into Aarhus from outside
# Denmark, which is unaffected by any later moves within Aarhus.
# AdresseAktuel is used to get the name and filter people who are dead, young or missing.
# Takes the earliest and latest arrival date to consider as parameters, in that order.
LETTER_RECEIVERS_QUERY = """
    WITH moves AS (
        SELECT *,
        LAG(Komkode) OVER (PARTITION BY CPR ORDER BY DatoTilflyt) AS from_kom_kode,
        LAG(Vejkode) OVER (PARTITION BY CPR ORDER BY DatoTilflyt) AS from_vej_kode,
        ROW_NUMBER() OVER (PARTITION BY CPR ORDER BY DatoTilflyt DESC) AS row_num
        FROM DWH.dwh.Flyttehistorik
    ),
    -- The latest move into Aarhus from outside Denmark, ignoring any moves within Aarhus since
    arrivals AS (
        SELECT CPR, MAX(DatoTilflyt) AS arrival_date
        FROM moves
        WHERE Komkode = '0751' -- Aarhus Kommune
            AND from_kom_kode NOT IN ('0101' ,'0147' ,'0151' ,'0153' ,'0155' ,'0157' ,'0159' ,'0161' ,'0163' ,'0165' ,'0167' ,'0169' ,'0173' ,'0175' ,'0183' ,'0185' ,'0187' ,'0190' ,'0201' ,'0210' ,'0217' ,'0219' ,'0223' ,'0230' ,'0240' ,'0250' ,'0253' ,'0259' ,'0260' ,'0265' ,'0269' ,'0270' ,'0306' ,'0316' ,'0320' ,'0326' ,'0329' ,'0330' ,'0336' ,'0340' ,'0350' ,'0360' ,'0370' ,'0376' ,'0390' ,'0400' ,'0410' ,'0411' ,'0420' ,'0430' ,'0440' ,'0450' ,'0461' ,'0479' ,'0480' ,'0482' ,'0492' ,'0510' ,'0530' ,'0540' ,'0550' ,'0561' ,'0563' ,'0573' ,'0575' ,'0580' ,'0607' ,'0615' ,'0621' ,'0630' ,'0657' ,'0661' ,'0665' ,'0671' ,'0706' ,'0707' ,'0710' ,'0727' ,'0730' ,'0740' ,'0741' ,'0746' ,'0751' ,'0756' ,'0760' ,'0766' ,'0773' ,'0779' ,'0787' ,'0791' ,'0810' ,'0813' ,'0820' ,'0825' ,'0840' ,'0846' ,'0849' ,'0851' ,'0860') -- Danish commune codes, so anything else is outside Denmark
            AND from_vej_kode NOT IN ('9902', '9901') -- Homeless and couch surfers
        GROUP BY CPR
    )
    SELECT
        arrivals.CPR,
        AdresseAktuel.Fornavn AS given_name,
        arrivals.arrival_date
    FROM arrivals
    INNER JOIN moves latest_move ON latest_move.CPR = arrivals.CPR AND latest_move.row_num = 1
    INNER JOIN DWH.Mart.AdresseAktuel ON AdresseAktuel.CPR = arrivals.CPR
    -- Only those who still live in the city
    WHERE latest_move.Komkode = '0751'
        AND latest_move.DatoFraflytAAK IS NULL
    -- The waiting period has passed, but the arrival isn't so old that we no longer care
        AND arrivals.arrival_date BETWEEN ? AND ?
    -- Sort on data from address database
        AND AdresseAktuel.Forsvundet = 0
        AND	AdresseAktuel.Doedsdato IS NULL
        AND	AdresseAktuel.Alder >= 18
        AND AdresseAktuel.HerkomstKode != DK
    """


def get_letter_receivers(min_days_since_arrival: int, max_days_since_arrival: int) -> list[pyodbc.Row]:
    """Get everyone whose welcome letter is due now.

    Args:
        min_days_since_arrival: How long to wait after a person arrived before their letter is due.
        max_days_since_arrival: How far back to look for arrivals, so we don't look through the entire move history.

    Returns:
        List of rows of cpr, first name and arrival date.
    """
    today = datetime.now()
    earliest_arrival = today - timedelta(days=max_days_since_arrival)
    latest_arrival = today - timedelta(days=min_days_since_arrival)

    connection = pyodbc.connect(CONNECTION_STRING)
    try:
        cursor = connection.cursor()
        cursor.execute(LETTER_RECEIVERS_QUERY, earliest_arrival, latest_arrival)
        return cursor.fetchall()
    finally:
        connection.close()
