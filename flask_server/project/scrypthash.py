import subprocess
import base91

def scrypt_hash(password,
	            salt,
	            n,
	            r,
	            p,
	            dklen):

    # We use the scrypt executable to generate the key in Base-91 format.
    
    os_command = ["scrypt-kdf", 
                  password,
                  salt,
                  str(n),
                  str(r),
                  str(p),
                  str(dklen * 8)]
       
    returned_string = str(subprocess.check_output(os_command))

    # The returned string is the following elements, separated by "-"
    # key salt logN r p
    # Key and salt are in base91 format
    returned_hash = returned_string.split("-")[0]
    byte_string = base91.decode(returned_hash)

    return byte_string

