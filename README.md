gnucash-toolset
===============

Access and manipulate gnucash data. 
Import JSON data into gnucash.

```
usage: gnucash-toolset [-h] [--loglevel LOGLEVEL]
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
                        get-bill       : Export a bill in a json file (out_file) from gnucash (in_file).
                        json-import    : Imports a json file (in_file) into gnucash (out_file).
  in_file               Path/file for input
  out_file              Path/file for output

optional arguments:
  -h, --help            show this help message and exit
  --loglevel LOGLEVEL   Log level
```
