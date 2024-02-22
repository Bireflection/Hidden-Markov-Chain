# Example SQL insert statement
with open('botnet.txt','r') as f:
    sql = f.readlines()
with open('md5.txt',"w") as f:
    for sql_insert in sql:

# sql_insert = "INSERT INTO `malware` VALUES ('2016-09-20 07:25:43', '0003d90b60fb6fdd467a0ae9eb46ef82', '66.147.107.178', 443, 'fbc551bfc06f94f9460eab402137685b565f3985');"

# # Extracting the specific part (e.g., '0003d90b60fb6fdd467a0ae9eb46ef82') from the string
# # We split the string by apostrophes and get the second element (index 1)
        extracted_part = sql_insert.split("'")[3]  # Index 3 because the desired part is after the third apostrophe
        print(extracted_part)
        f.write(extracted_part + "\n")


# extracted_part

