# coding: utf-8

SQL_SHOPS = '''
select 
    kod as ourCode, 
    kod as theyCode, 
    regtrans as shopRegion, 
    kodorg, 
    manager 
from [..\\REFLIS\\DICT.ADD].R20 
where shadow <> 1 and kod <> 0
'''

SQL_SHOPS_CLIENT = '''
select 
    kod as ourCode, 
    INSIDEKOD as theyCode, 
    regtrans as shopRegion, 
    kodorg, 
    manager 
from [..\\REFLIS\\DICT.ADD].R20 
where shadow <> 1 and kod <> 0 and INSIDEKOD <> 0 and kodorg = ? 
'''

SQL_SHOPS_FERMER = u'''
SELECT 
    KOD AS ourCode, 
    INSIDEKOD AS theyCode, 
    REGTRANS AS shopRegion, 
    kodorg, 
    manager 
FROM [..\\REFLIS\\DICT.ADD].R20 
WHERE SHADOW <> 1 AND KOD <> 0 AND INSIDEKOD <> 0 AND UPPER(PNAME) LIKE '%ФЕРМЕР%' 
'''

SQL_PRODS = '''
SELECT \
    R11.KOD AS ourCode, 
    R11.KOD AS theyCode,
    100 as koef, 
    R11.NORM_UKL AS packSize,  
    R11.WEIGHT AS prodWeight, 
    R11.USE_STATUS as uses, 
    R11.EXPANAL as exp, 
    R11.CODEGROUP as codeGroup, 
    R11.PROD_TYPE AS prodType 
from [..\\reflis\\dict.add].R11 
where shadow <> 1 
'''

SQL_PRODS_CLIENT = '''
SELECT 
    CASE WHEN R329.KODPROD IN (6036) THEN 2153  
        ELSE R329.KODPROD 
    END ourCode, 
    R329.KODPROD AS ourCode, 
    CAST(R329.OUT_CODE AS SQL_NUMERIC(20,0)) AS theyCode, 
    100 koef, 
    R11.NORM_UKL AS packSize, 
    R11.WEIGHT AS prodWeight, 
    R11.USE_STATUS as uses,
    R11.EXPANAL as exp, 
    R11.CODEGROUP as codeGroup, 
    R11.PROD_TYPE AS prodType 	
FROM ( 
    SELECT 
        KODORG, 
        OUT_CODE, 
        MAX(PRIORITY) PRIORITY 
    FROM [..\\REFLIS\\DICT.ADD].R329 
    WHERE OUT_CODE <> '' AND KODORG = ? 
    GROUP BY 1,2 
) CODES 
LEFT JOIN [..\\REFLIS\\DICT.ADD].R329 ON R329.OUT_CODE = CODES.OUT_CODE 
    AND R329.PRIORITY = CODES.PRIORITY 
LEFT JOIN [..\\REFLIS\\DICT.ADD].R11 ON R11.KOD = KODPROD 
WHERE R329.KODORG = ? 
'''

SQL_SET_PACK = '''
UPDATE [..\\USERDATA\\USERDATA.ADD].IMPORTED_ORDERS 
SET PACKVALUE = ? 
WHERE ID IN ( 
    SELECT MAX(ID) AS MAX_ID 
    FROM [..\\USERDATA\\USERDATA.ADD].IMPORTED_ORDERS 
    WHERE 1 = 1 AND ORDERDATE = ? 
    GROUP BY ORDERTIME, SHOP 
    HAVING SUM(PACKVALUE) = 0 
); 
'''

SQL_ALREADY_LOADED = '''
select count(distinct shop) as cnt 
from [..\\userdata\\userdata.add].imported_orders 
where fileName = ? and orderdate = ? 
'''

SQL_ALREADY_LOADED_PROD = '''
select prod, shop, fileName, sum(prodvalue) as amnt 
from [..\\userdata\\userdata.add].imported_orders
where orderdate = ? 
group by 1, 2, 3
'''

SQL_INSERT_PROD_PRM = '''
insert into [..\\UserData\\UserData.add].imported_orders 
(orderDate, orderTime, client, shop, prod, prodWeight, packSize, packValue, prodValue, fileName, lineNumber, theyProd, theyProdName, theyShop, theyShopName, isMgrOrder, manager, isReject, note) values \n
(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);\n
'''

SQL_INSERT_PROD = '''
insert into [..\\UserData\\UserData.add].imported_orders 
(orderDate, orderTime, client, shop, prod, prodWeight, packSize, packValue, prodValue, fileName, lineNumber, theyProd, theyProdName, theyShop, theyShopName, isMgrOrder, manager, isReject, note) values
(':orderDate', :orderTime, :client, :shop, :prod, :prodWeight, :packSize, :packValue, :prodValue, ':fileName', :lineNumber, ':theyProd', ':theyProdName', ':theyShop', ':theyShopName', :isMgrOrder, :manager, :isReject, ':note');\n
'''