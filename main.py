import dropbox
#dbx = dropbox.Dropbox('YOUR_ACCESS_TOKEN')
dbx = dropbox.Dropbox('iTG45yQvU6sAAAAAAAAFZ2miQx9MlrEpJsXYb6Lf44YLfsoLkfslAE9c6kDpQzPV')
dbx.users_get_current_account()
for entry in dbx.files_list_folder('').entries:
    print(entry.name)