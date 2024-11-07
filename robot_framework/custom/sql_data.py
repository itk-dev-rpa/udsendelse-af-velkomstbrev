import pyodbc


def sql_query(date: str) -> str:
    return f"""
-- SQL Expression used to find people who moved into the commune, filtered by last address and other factors
-- Three databases are joined: current_address, previous_address and AdresseAktuel.
-- current_address show the citizens who moved into the commune
-- previous_address contains from where the citizen last moved, to differentiate between in- and out of the country
-- AdresseAktuel contains more data, and we get the name of the person from here, as well as filter dead, missing and young people

-- Get sequence of relocations for each person, only look at the current and last address
WITH CTE AS (
    SELECT *,
    ROW_NUMBER() OVER (PARTITION BY CPR ORDER BY DatoTilflyt DESC) AS row_num
    FROM DWH.dwh.Flyttehistorik
)
SELECT current_address.CPR,
    current_address.DatoTilflyt AS latest_move_date,
    previous_address.DatoTilflyt AS second_latest_move_date,
    AdresseAktuel.Fornavn AS given_name
FROM CTE current_address
LEFT JOIN CTE previous_address ON current_address.CPR = previous_address.CPR AND current_address.row_num = 1 AND previous_address.row_num = 2
INNER JOIN DWH.Mart.AdresseAktuel ON AdresseAktuel.CPR = current_address.CPR
WHERE current_address.Komkode = '0751' -- Aarhus Kommune
    AND current_address.DatoTilflyt > Convert(datetime, '{date}')
    AND current_address.DatoFraflytAAK IS NULL
-- Only look at those whose previous address is in Denmark
    AND previous_address.Komkode IN ('0101' ,'0147' ,'0151' ,'0153' ,'0155' ,'0157' ,'0159' ,'0161' ,'0163' ,'0165' ,'0167' ,'0169' ,'0173' ,'0175' ,'0183' ,'0185' ,'0187' ,'0190' ,'0201' ,'0210' ,'0217' ,'0219' ,'0223' ,'0230' ,'0240' ,'0250' ,'0253' ,'0259' ,'0260' ,'0265' ,'0269' ,'0270' ,'0306' ,'0316' ,'0320' ,'0326' ,'0329' ,'0330' ,'0336' ,'0340' ,'0350' ,'0360' ,'0370' ,'0376' ,'0390' ,'0400' ,'0410' ,'0411' ,'0420' ,'0430' ,'0440' ,'0450' ,'0461' ,'0479' ,'0480' ,'0482' ,'0492' ,'0510' ,'0530' ,'0540' ,'0550' ,'0561' ,'0563' ,'0573' ,'0575' ,'0580' ,'0607' ,'0615' ,'0621' ,'0630' ,'0657' ,'0661' ,'0665' ,'0671' ,'0706' ,'0707' ,'0710' ,'0727' ,'0730' ,'0740' ,'0741' ,'0746' ,'0756' ,'0760' ,'0766' ,'0773' ,'0779' ,'0787' ,'0791' ,'0810' ,'0813' ,'0820' ,'0825' ,'0840' ,'0846' ,'0849' ,'0851' ,'0860') -- Danish commune codes
    AND previous_address.Vejkode NOT IN ('9902', '9901') -- Homeless and couch surfers
-- Sort on data from address database
    AND AdresseAktuel.Forsvundet = 0
    AND	AdresseAktuel.Doedsdato IS NULL
    AND	AdresseAktuel.Alder >= 18
"""


def read_data(query: str) -> list[pyodbc.Row]:
    cn = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER=FaellesSQL;DATABASE=DWH;Trusted_Connection=yes")
    cursor = cn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return data


def sql_to_dict(data: list[pyodbc.Row]) -> dict:
    id_names = {}
    for row in data:
        id_names[row[0]] = row[3]
    return id_names
