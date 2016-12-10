from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse,HttpResponseNotFound
from models import Issue,Repository,Board,ReadPermissions,OauthCheck
from django.utils.cache import add_never_cache_headers
import requests
from django.contrib.auth.decorators import login_required
from myproject import settings
from forms import Repoform,Boardform,Userform
import re
import random
import string

#GITHUB_USER = settings.GITHUB_USER
#GITHUB_PASSWORD = settings.GITHUB_PASSWORD
#AUTH = (settings.GITHUB_USER, settings.GITHUB_PASSWORD)

#COMPANY = settings.COMPANY
#REPOS = settings.REPOS
           
def get_issues(r,REPO):
  "output a list of issues to csv"
  print REPO
  if not r.status_code == 200:
    raise Exception(r.status_code)
  ret = r.json()
  for issue in ret:
    issue["repository"] = REPO
  return ret
#    for issue in r.json():
#        labels = issue['state']
#        #for label in labels:
#        #if label['name'] == "Client Requested":
#        if issue['state'] == 'open':
#            #csvout.writerow([issue['number'], issue['title'].encode('utf-8'), issue['body'].encode('utf-8'), issue['created_at'], issue['updated_at']])
#            csvout.writerow([ str(x).replace(',','-') for x in [REPO, issue['number'], issue['title'].encode('utf-8'), issue['url'], issue['created_at'], issue['updated_at']]])
# 
def pull_issues(REPO, access_token, token_type):
  ISSUES_FOR_REPO_URL = 'https://api.github.com/repos/%s/issues' % REPO
  r = requests.get(ISSUES_FOR_REPO_URL, headers={'Authorization': token_type+" "+access_token})
  issues=[]
  issues.extend(get_issues(r,REPO))

  #more pages? examine the 'link' header returned
  if 'link' in r.headers:
    pages = dict(
      [(rel[6:-1], url[url.index('<')+1:-1]) for url, rel in
        [link.split(';') for link in
        r.headers['link'].split(',')]])
    while 'last' in pages and 'next' in pages:
      r = requests.get(pages['next'], headers={'Authorization': token_type+" "+access_token})
      issues.extend(get_issues(r,REPO))
      if pages['next'] == pages['last']:
        break
  return issues

def create_new(board, issue, user):
  saved = Issue()
  saved.board = board
  saved.repository = issue['repository']
  saved.issueid = str(issue['number'])
  saved.title = str(issue['title'].encode('utf-8'))
  saved.url = "https://github.com/"+issue['repository']+"/issues/"+str(issue['number'])
  saved.created = issue['created_at'].split("T")[0]
  saved.updated = issue['updated_at'].split("T")[0]
  if "assignee" not in issue or not issue["assignee"]:
    saved.assigned="None"
  else:
    print issue['assignee']
    saved.assigned = issue['assignee']['login']
  saved.status = issue['state']
  saved.changed = False
  saved.release = "New"
  saved.comments = "None"
  saved.save()
   
def copy_existing(saved,issue,user):
  saved.changed = False
  if saved.repository != issue['repository']:
    saved.changed = True
    saved.repository = issue['repository']
  if saved.issueid != str(issue['number']):
    saved.changed = True
    saved.issueid = str(issue['number'])
  if saved.title != str(issue['title'].encode('utf-8')):
    saved.changed = True
    saved.title = str(issue['title'].encode('utf-8'))
  if saved.url != "https://github.com/"+issue['repository']+"/issues/"+str(issue['number']):
    saved.changed = True
    saved.url = issue['url']
  if saved.created != issue['created_at'].split("T")[0]:
    saved.changed = True
    saved.created = issue['created_at'].split("T")[0]
  if saved.updated != issue['updated_at'].split("T")[0]:
    saved.changed = True
    saved.updated = issue['updated_at'].split("T")[0]
  if "assignee" not in issue or not issue["assignee"]:
    saved.assigned="None"
  else:
    if saved.assigned != issue["assignee"]["login"]:
      saved.changed = True
      saved.assigned = issue['assignee']['login']
  if saved.status != issue['state']:
    saved.changed = True
    saved.status = issue['state']
  saved.save()

# Create your views here.
@login_required(login_url=('/login/'))
def issues_refresh(request,boardid):
  boards = Board.objects.filter(pk=boardid)
  filt = request.GET.get("filter","")
  if len(boards) == 0:
    ret  = HttpResponseRedirect("/issueview/board/show/")
    add_never_cache_headers(ret)
    return ret
  if boards[0].user != request.user and len(ReadPermissions.objects.filter(username=request.user.username).filter(board_id = boardid)) == 0:
    ret  = HttpResponseRedirect("/issueview/board/show/")
    add_never_cache_headers(ret)
    return ret
  REPOS=[x.repository for x in Repository.objects.filter(board=boards[0])]
  issues=[]
  for i in REPOS:
    issues.extend(pull_issues(i))
  for issue in issues:
    saved_issue = Issue.objects.filter(board=boards[0]).filter(issueid = str(issue['number'])).filter(repository=str(issue['repository']))      
    if len(saved_issue) > 0:
      copy_existing(saved_issue[0], issue, request.user)
    else:
      create_new(boards[0], issue, request.user)
  filtstring=""
  if len(filt) > 0:
    filtstring="?filter="+filt
  ret  = HttpResponseRedirect("/issueview/show/"+boards[0].user.username+"/"+boards[0].board+"/"+filtstring)
  add_never_cache_headers(ret)
  return ret

@login_required(login_url=('/login/'))
def issues_update(request,issueid):
  if request.method == "POST":
    issue = Issue.objects.get(pk=issueid)
    if issue.user != request.user and len(ReadPermissions.objects.filter(username=request.user.username).filter(board = issue.board)) == 0:
      ret  = HttpResponseRedirect("/issueview/board/show/")
      add_never_cache_headers(ret)
      return ret
    release = request.POST.get('release') 
    comments = request.POST.get('comments')
    issue.release = release
    issue.comments = comments
    issue.save()
    filt = request.POST.get("filter","")
    filtstring=""
    if len(filt) > 0:
      filtstring="?filter="+filt
    ret = HttpResponseRedirect("/issueview/show/"+issue.board.user.username+"/"+issue.board.board+"/"+filtstring)
    add_never_cache_headers(ret)
    return ret
  ret = HttpResponseRedirect("/issueview/board/show/")
  add_never_cache_headers(ret)
  return ret

def apply_filter(issues, filt):
  filtlist = filt.split(",")
  print "filt:"+str(filtlist)
  for f in filtlist:
    fvals = f.split(":")
    fname = fvals[0]
    fv = fvals[1]
    print fname+":"+fv
    if fname == 'release':
      issues= issues.filter(release=fv)
    elif fname == 'assigned':
      issues= issues.filter(assigned=fv)
    elif fname == 'status':
      issues= issues.filter(status=fv)
    elif fname == 'repository':
      issues= issues.filter(repository=fv)
  return issues

@login_required(login_url=('/login/'))
def issues_show(request, owner, board):
  if request.method == "GET":
    boards = Board.objects.filter(board=board).filter(user__username=owner)
    if len(boards) == 0:
      ret = HttpResponseRedirect('/issueview/board/show/')
      add_never_cache_headers(ret)
      return ret 
    
    if boards[0].user != request.user and len(ReadPermissions.objects.filter(username=request.user.username).filter(board = boards[0])) == 0:
      ret  = HttpResponseRedirect("/issueview/board/show/")
      add_never_cache_headers(ret)
      return ret

    is_self = True

    if boards[0].user != request.user:
      is_self = False

    repos = Repository.objects.filter(board__board=board).filter(board__user=request.user)
    filt = request.GET.get("filter","")
    issue_list = Issue.objects.filter(board__board=board)
    users = ReadPermissions.objects.filter(board=boards[0])
    if filt != "":
      issue_list = apply_filter(issue_list, str(filt))
    randomstr = ''.join(random.choice(string.letters) for i in xrange(10))
    board_state_secret=str(boards[0].id)+"~"+str(filt)+"~"+randomstr
    oauth_details = OauthCheck()
    oauth_details.user = request.user
    oauth_details.state = board_state_secret
    oauth_details.save() 
    ret =  render(request, "issueview/list.html", { "client_secret": settings.CLIENT_ID, 
                                                    "board_state_secret": board_state_secret,
                                                    "userform": Userform(), 
                                                    "issues":issue_list,
                                                    "filtstring":str(filt),
                                                    "users" : users,
                                                    "repos": repos,
                                                    "board": boards[0],
                                                    "isself": is_self})
    add_never_cache_headers(ret)
    return ret

@login_required(login_url=('/login/'))
def issues_repos(request, board):
  boards = Board.objects.filter(board=board).filter(user=request.user)
  if len(boards) == 0: 
    ret = HttpResponseRedirect('/issueview/board/show/')
    add_never_cache_headers(ret)
    return ret 

  if request.method == "GET":
    filtstring=request.GET.get("filter","")
    repos = Repository.objects.filter(board__user = request.user).filter(board__board=board)
    form = Repoform()
    ret = render(request,"issueview/repos.html",{"board": boards[0],
                                                 "form": form,
                                                 "repos": repos,
                                                 "filtstring": filtstring})
    add_never_cache_headers(ret)
    return ret
  form = Repoform(request.POST)
  filtstring = request.POST.get("filter","")
  if form.is_valid():
    newrepo = Repository()
    newrepo.repository = form.cleaned_data["repository"]
    newrepo.board = boards[0]
    newrepo.save()
    form = Repoform()
  repos = Repository.objects.filter(board__user = request.user)
  ret = render(request,"issueview/repos.html",{"board": boards[0],
                                               "form": form,
                                               "repos": repos,
                                               "filtstring": filtstring})
  add_never_cache_headers(ret)
  return ret 

@login_required(login_url=('/login/'))
def issues_authorize(request):
  if request.method == "GET":
    code = request.GET.get('code','')
    state = request.GET.get('state','')
    try:
      oauth_details = OauthCheck.objects.get(state=state,user=request.user)
      oauth_details.delete()
    except:
      ret = HttpResponseRedirect('/issueview/board/show/')
      add_never_cache_headers(ret)
      return ret 
    r = requests.post("https://github.com/login/oauth/access_token",
      {"client_id": settings.CLIENT_ID,
       "client_secret":settings.CLIENT_SECRET,
       "code":code,
       "state":state }, headers={'Accept': 'application/json'})
    response = r.json()
    if 'repo' not in response['scope'].split(','):
      # not authenticated, so print a message and end it.
      ret = HttpResponse('Failed to authorize. Exitting.')
      add_never_cache_headers(ret)
      return ret 
    #fully authorized
    access_token = response["access_token"]
    token_type = response["token_type"]
    boardid = state.split("~")[0]
    filt = state.split("~")[1]

    board = Board.objects.get(pk=boardid)
    REPOS=[x.repository for x in Repository.objects.filter(board=board)]
    issues=[]
    for i in REPOS:
      issues.extend(pull_issues(i,access_token, token_type))
    for issue in issues:
      saved_issue = Issue.objects.filter(board=board).filter(issueid = str(issue['number'])).filter(repository=str(issue['repository']))      
      if len(saved_issue) > 0:
        copy_existing(saved_issue[0], issue, board.user)
      else:
        create_new(board, issue, request.user)
    filtstring=""
    if len(filt) > 0:
      filtstring="?filter="+filt
    ret  = HttpResponseRedirect("/issueview/show/"+board.user.username+"/"+board.board+"/"+filtstring)
    add_never_cache_headers(ret)
    return ret

 

@login_required(login_url=('/login/'))
def issues_repo_delete(request, boardid, repoid):
  board = Board.objects.filter(pk=boardid)
  if board.user != request.user and len(ReadPermissions.objects.filter(username=request.user.username).filter(board_id = boardid)) == 0:
    ret = HttpResponseRedirect('/issueview/board/show/')
    add_never_cache_headers(ret)
    return ret 
  repo = Repository.objects.filter(board__user=board.user).filter(pk=repoid)
  if len(repo) == 0:
    ret = HttpResponseRedirect('/issueview/repos/'+boardid+"/")
    add_never_cache_headers(ret)
    return ret 
  repo[0].delete()
  filtstring = request.GET.get("filter","")
  if len(filtstring):
    ret = HttpResponseRedirect('/issueview/repos/'+boardid+"/"+"?filter="+filtstring)
  else:
    ret = HttpResponseRedirect('/issueview/repos/'+board+"/")
  add_never_cache_headers(ret)
  return ret 
 
valid_board_re = re.compile("[a-z0-9_]+$")
def valid_board(board, user):
  m = valid_board_re.match(board)
  if not m:
    return False
  if len(m.group(0)) != len(board):
    return False
  boards = Board.objects.filter(user=user).filter(board=board)
  if len(boards) == 0:
    return True
  return False

@login_required(login_url=('/login/'))
def show_board(request):
  if request.method == "GET":
    boards = Board.objects.filter(user = request.user)
    form = Boardform()
    shared = ReadPermissions.objects.filter(username=request.user.username)
    ret = render(request,"issueview/boards.html",{"form": form,
                                                 "boards": boards,
                                                 "shared": shared})
    add_never_cache_headers(ret)
    return ret
  form = Boardform(request.POST)
  if form.is_valid(): 
    if valid_board(form.cleaned_data["board"],request.user):
      board = Board()
      board.board = form.cleaned_data["board"]
      board.user = request.user
      board.save()
      form = Boardform()
    else:
      form.add_error(None,"board names should be unique and should only use small case digits, alphabet and underscore.")
  boards = Board.objects.filter(user = request.user)
  shared = ReadPermissions.objects.filter(username=request.user.username)
  ret = render(request,"issueview/boards.html",{"form": form,
                                               "boards": boards,
                                               "shared": shared})
  add_never_cache_headers(ret)
  return ret 


@login_required(login_url=('/login/'))
def del_board(request, boardid):
  boards = Board.objects.filter(user=request.user).filter(pk=boardid)
  if len(boards) == 0:
    ret = HttpResponseRedirect('/issueview/board/show/')
    add_never_cache_headers(ret)
    return ret 
  boards[0].delete()
  ret = HttpResponseRedirect('/issueview/board/show/')
  add_never_cache_headers(ret)
  return ret 

@login_required(login_url=('/login/'))
def edit_board(request, boardid):
  boards = Board.objects.filter(user = request.user).filter(pk=boardid)
  if len(boards) == 0:
    ret = HttpResponseRedirect('/issueview/board/show/')
    add_never_cache_headers(ret)
    return ret 
    
  if request.method == "GET":
    form = Boardform(initial={"board":boards[0].board})
    ret = render(request,"issueview/board_edit.html",{"form": form, "board":boards[0]})
    add_never_cache_headers(ret)
    return ret
  form = Boardform(request.POST)
  if form.is_valid(): 
    if boards[0].board == form.cleaned_data["board"] or valid_board(form.cleaned_data["board"],request.user):
      board = boards[0]
      board.board = form.cleaned_data["board"]
      board.user = request.user
      board.save()
      ret = HttpResponseRedirect('/issueview/board/show/')
      add_never_cache_headers(ret)
      return ret 
    else:
      form.add_error(None,"board names should be unique and should only use small case digits, alphabet and underscore.")
  ret = render(request,"issueview/board_edit.html",{"form": form, "board":boards[0]})
  add_never_cache_headers(ret)
  return ret 

@login_required(login_url=('/login/'))
def user_add(request, boardid):
  if request.method == "POST":
    filtstring = request.POST.get("filter","")
    boards = Board.objects.filter(pk=boardid)
    if boards[0].user != request.user and len(ReadPermissions.objects.filter(username=request.user.username).filter(board_id = boardid)) == 0:
      ret = HttpResponseRedirect('/issueview/board/show/')
      add_never_cache_headers(ret)
      return ret 
    userform = Userform(request.POST)
    if userform.is_valid():
      print "Valid:" + userform.cleaned_data["username"]
      newuser = ReadPermissions()
      newuser.board = boards[0]
      newuser.username = userform.cleaned_data["username"]
      newuser.save()
    if len(filtstring) > 0:
      filtstring = "?filter="+filtstring
    ret  = HttpResponseRedirect("/issueview/show/"+boards[0].user.username+"/"+boards[0].board+"/"+filtstring)
    add_never_cache_headers(ret)
    return ret

@login_required(login_url=('/login/'))
def user_del(request, boardid, userid):
  filtstring = request.GET.get("filter","")
  boards = Board.objects.filter(pk=boardid)
  if boards[0].user != request.user and len(ReadPermissions.objects.filter(username=request.user.username).filter(board_id = boardid)) == 0:
      ret = HttpResponseRedirect('/issueview/board/show/')
      add_never_cache_headers(ret)
      return ret 
  readperm = ReadPermissions.objects.filter(pk=userid)
  if readperm[0].board == boards[0]:
    readperm[0].delete()
  if len(filtstring) > 0:
    filtstring = "?filter="+filtstring
  ret  = HttpResponseRedirect("/issueview/show/"+boards[0].user.username+"/"+boards[0].board+"/"+filtstring)
  add_never_cache_headers(ret)
  return ret
