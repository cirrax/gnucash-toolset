gnucash-toolset
===============

Access and manipulate gnucash data. 
Import JSON data into gnucash.

```
usage: gnucash-toolset [-h] [--loglevel LOGLEVEL] [--template TEMPLATE]
                       [--invoice INVOICE] [--date_format DATE_FORMAT]
                       {csv-customers,csv-vendors,get-bill,create-copy,json-import}
                       in_file out_file

Gnucash toolset to export/manipulate gnucash data

positional arguments:
  {csv-customers,csv-vendors,get-bill,create-copy,json-import}
                        Commands to execute:
                        csv-customers  : Create a CSV file with all customers. Ready to import with gnucash.
                        csv-vendors    : Create a CSV file with all vendors. Ready to import with gnucash.
                        create-copy    : Create a copy of gnucash data. Data copied are: Accounts, Customers, Vendors.
                                         Data NOT copied: Bookings, Invoices, Bills, Transactions.
                                         Data to be copied, but not yet implemented: Terms, Taxes, Employees, Jobs, Options.
                                         This can be used to create a new file after closing period.
                        copy-opening   : copy opening-amounts from another gnucash instance. (Not yet implemented).
                        get-bill       : Export a bill from gnucash (in_file) into a jinja template.
                        json-import    : Imports a json file (in_file) into gnucash (out_file).
  in_file               Path/file for input
  out_file              Path/file for output

optional arguments:
  -h, --help            show this help message and exit
  --loglevel LOGLEVEL   Log level
  --template TEMPLATE   jinja2 template to use for get-bill
  --invoice INVOICE     invoice ID to usefor get-bill
  --date_format DATE_FORMAT
                        Date format in JSON parts/files.
```

Example JSON file for import:
-----------------------------
```
[
  {
    "invoice": { "CustomerID"    : "000001",
                 "Notes"         : "Billing Notes",
                 "JobID"         : "if-jobid-customerID-is ignored",
                 "AReceivableAC" : "1100",
                 "entries"       : [ {
                        "Description" : "Invoice entry description",
                        "Action"      : "Hours",
                        "Notes"       : "Entry Notes",
                        "Price"       : 99.95,
                        "IncomeAC"    : "3000",
                        "TaxIncluded" : false,
                        "Taxable"     : true,
                        "Quantity"    : 10,
                        "TaxName"     : "MwSt 8%"
                   } ]
               }
  },
  {
    "transfer": {
        "Num"           : "Number",
        "Amount"        : 100.45
        "Date"          : "2015-04-14",
        "Memo"          : "transfer from 1020 to 1025",
        "Description"   : "transfer",
        "TransferFromAC": "1020",
        "TransferToAC"  : "1025"
     }
  },
  {
    "payment": {
        "BillID"        : "150007",
        "Amount"        : 100.45
        "Date"          : "2015-03-14",
        "Memo"          : "payment of Bill 150007",
        "TransferAC"    : "1020"
     }
  }
]
```
