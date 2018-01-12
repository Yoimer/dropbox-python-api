import dropbox
#dbx = dropbox.Dropbox('YOUR_ACCESS_TOKEN')
dbx = dropbox.Dropbox('iTG45yQvU6sAAAAAAAAFZ2miQx9MlrEpJsXYb6Lf44YLfsoLkfslAE9c6kDpQzPV')
dbx.users_get_current_account()

# empty means root directoty (/root)
#for entry in dbx.files_list_folder('').entries:

# this is an especific folder
for entry in dbx.files_list_folder('/Apps/yoimer1').entries:
    print(entry.name)