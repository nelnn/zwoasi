## git clone
If you want to clone the repository to the local computer, simply use *git clone*. For example,
```console
$ git clone https://github.com/hkspm-yp/ZWO.git
```
## git add, git commit, git push
- git add \<filename>: to track the file you have modified
- git status: see what changes are tracked
- git commit -m "some comments": commit your changes
- git push: push your commit to the repository

Example: 
```console
$ git add .   # track all the files
$ git commit -m "added xyz features"
$ git push    # or git push origin main
```
## Credentials
```
hkspm account
username: hkspm-yp
password: 273427yp
token: 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
```
git will ask for your credential if you are pushing in the terminal. **DO NOT** enter the account password, use the token instead. If the token expires, generates a new one in 
```
github settings -> developer settings -> personal access tokens
```
Alternatively, you can set up a public SSH key so you won't need to provide your credentials every time you push/pull.

side note: vscode has built in git, if you push for thr first time it will redirect you to the github login page. You need to login for once only. After that you can use git in the vscode terminal without providing username and access token.

## git branch
git branch is great when you want to work on some new features without affecting the current working scripts.
```console
$ git branch # check which branch you are in
$ git checkout -b test-branch # make a new branch named test-branch.
$ git checkout test-branch # go to test-branch
```
Commit your changes as usual
```console
$ git add .
$ git commit -m "new features added"
$ git push --set-upstream origin test-branch # push it to a remote upstream named test-branch
```
When you clone the repository for the first time, only the main branch is fetched. If you run
```console
$ git branch -a
```
it will show the remote branches that have not yet been fetch. To pull, just type
```console
$ git check-out remote-branch-name
```

## git merge
Once you are happy with the changes in the test-branch, you can merge it with the main branch so now you can run the lastest version of the code. Make sure you have commited all changes in test-branch before merging.
```console
$ git checkout main
$ git pull origin main
$ git merge test-branch
$ git push origin main
```
## .gitignore
It contains file/folder names that you **don't** want to push to the remote respository, i.e. these files/folders are stored in the local machine only. For example, you want to ignore the \__pycache__ folder since it's not necessary. Following is an example of what a .gitignore contains for the all sky camera project.

```console
__pycache__/
photos/
data.csv
errorLog.txt
source/*.jpg
```
If you updated the gitignore, remember to commit everything you've changed before you do the following:
```console
$ git rm -rf --cached .
$ git add .
```
