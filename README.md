CLI password manager

usage:
```bash
password.py [-h] [-e email] [-l login] [-s site] [-p password] [-d description] {add,edit,del,srch}
```

positional arguments:
  {add,edit,del,srch}
    add                Add new password to database
    edit               Edit record from database
    del                Delete password from database
    srch               Search password from database

optional arguments:
  -h, --help           show this help message and exit
  -e email             use to add email or search on it
  -l login             use to add login or search on it
  -s site              use to add site or search on it
  -p password                 use to add password
  -d description       use to add short description or search on it with
                       regexp

Also if you want to hash your passwords you can write hash function in file hash_func.py
