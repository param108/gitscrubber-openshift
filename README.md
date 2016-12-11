GitScrubber
===================

Collect all the issues from your git repositories.
Add your own data to issues to track progress. Add tags without messing up what the developers see.

__Important URLS__
_admin login_
gitscrub-paramsmvp.rhcloud.com/admin/

_login and see your boards and registration_
gitscrub-paramsmvp.rhcloud.com/

_list the boards you have_
gitscrub-paramsmvp.rhcloud.com/issueview/board/show/

* Decide which repositories you would like to have on the chart and use **Edit Repos** button to add them.


Repository naming should include the username or company
_For example_ param108/gitscrubber-openshift


* Decide who should be able to view the board. 

Just input the username and click add. You need to type the exact username. The user need not be logged in yet, when he logs in it will connect.

* Click **Refresh**

You will be redirected to github and asked for permissions to access repository data.

* See all your open issues get populated in a table format


* Use Release and Comments to track your issues

Release should be a single word [A-Za-z0-9\_] only (alphanumeric characters and underscore only. NO SPACES)
Comments are free hand text. Expand the text box if required. Write whatever.

* Filtering 

You can filter on assigned,release,status,repository,labels in any fashion. Labels have the additional functionality that they you filter on multiple labels and the tool also supports negative matches for labels.

  * Multiple search for labels

You can do multiple label matching using a "," seperated list.

_bug,help wanted_

will search for both "bug" and "help wanted". please avoid unnecessary whitespace.

  * Exclusion search for labels

If you wish to find all bugs without a particular label just add "^" to the front of the label.

_^bug,help wanted_

means search for issues without label "bug", but with label "help wanted"

similarly

_bug,^help wanted_

means search for issues with "bug" but without "help wanted"

