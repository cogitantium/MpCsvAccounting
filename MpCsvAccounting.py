import csv
from pathlib import Path
import locale
import datetime

def prepareCsvReader(filePath):
    file = open(filePath, "r", newline='', encoding="utf-16-le")
    next(file)
    next(file)

    return csv.reader(file, delimiter=";")

def readTransactionsFromFile(filePath):
    transactions = []
    registrationTransfers = []
    reader = prepareCsvReader(filePath)
    
    for row in reader:
        if row[0] == "Refundering" or row[0] == "Gebyr":
            continue
        if "tilmeld" in row[9].lower() or "indmeld" in row[9].lower():
            registrationTransfers.append(row[6])
            continue
        if row[0] == "Salg":
            continue

        transactions.append([row[3], row[6], row[10]])

    return transactions, registrationTransfers

def prepareCsvWriter(filePath):
    file = open(filePath, "w", newline='')
    csvWriter = csv.writer(file, delimiter=";")
    return csvWriter

def floatToLocalStringFloat(float):
    return str(float).replace(".", ",")

def writeTransactions(filePath, appendixStart, transactions, registrationTransferCounts):
    currTransferIndex = 0
    currAppendix = appendixStart
    csvWriter = prepareCsvWriter(filePath)

    csvWriter.writerow(["Bilag nr.", "Dato", "Tekst", "Konto", "Beløb", "Modkonto"])

    for i, transaction in enumerate(transactions):
        # A registration transfer can happen a number of times in a day
        registrationTransferDate = registrationTransferCounts[0][0]
        numberOfRegistrationsInDay = int(registrationTransferCounts[0][1])
        transAmount = locale.atof(transaction[0])
        voucherAmount = transAmount + locale.atof(transaction[2])
        transactionDate = datetime.datetime.strptime(transaction[1], "%d-%m-%Y")
        headlineDate = str(transactionDate.day) + "-" + str(transactionDate.month)
        
        csvWriter.writerow([currAppendix, transaction[1], "MP " + headlineDate.zfill(5), "55000", floatToLocalStringFloat(transAmount), None])
        
        if transaction[1] != registrationTransferDate:
            csvWriter.writerow([currAppendix, transaction[1], "Gavekort", "63080", "-" + floatToLocalStringFloat(voucherAmount), None])
        else:
            registrationFees = 200*numberOfRegistrationsInDay
            voucherAmount = transAmount + locale.atof(transaction[2]) - registrationFees

            csvWriter.writerow([currAppendix, transaction[1], "Gavekort", "63080", "-" + floatToLocalStringFloat(voucherAmount), None])
            csvWriter.writerow([currAppendix, registrationTransferDate, "Tilmeldingsgebyr", "1000", "-" + floatToLocalStringFloat(registrationFees), None])

            registrationTransferCounts.pop(0)

        csvWriter.writerow([currAppendix, transaction[1], "MP-gebyr", "7220", transaction[2], None])

        currAppendix += 1

def main():
    locale.setlocale(locale.LC_NUMERIC, "en_DK.UTF-8")

    filename = input("File name (on Desktop):\n> ")
    appendixStart = int(input("\nAppendix number start:\n> "))
    readPath = str(Path.cwd()) + "/" + filename
    writePath = str(Path.cwd()) + "/dinero_" + filename

    transactions, registrationTransfers = readTransactionsFromFile(readPath)

    registrationTransferCounts = [[transfer, registrationTransfers.count(transfer)] for transfer in set(registrationTransfers)]
    registrationTransferCounts.sort(key=lambda x: x[0])

    writeTransactions(writePath, appendixStart, transactions, registrationTransferCounts)

    print("\nDone writing to " + writePath)


if __name__ == "__main__":
    main()