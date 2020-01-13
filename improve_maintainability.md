As a part of the report, I suggest making the following changes:

#### Create helper method for get_object_by_pk
For a code as:
```python
try:
    obj = DjangoModelName.objects.get(
	    pk=django_model_name_pk
	  )
except DjangoModelName.DoesNotExist:
    response_data = {"error": "DjangoModelName does not exist"}
    return Response(response_data, HTTP.406_NOT_ACCEPTABLE)   
```
This type of code has been used in several places throughout the codebase in challenges/views.py, jobs/views.py, hosts/views.py, participants/views.py

Note: For consistency and keeping helper functions on same level of abstraction, a similar helper function for `DjangoModel.objects.filter` should be considered.
#### Remove code duplication
Remove code duplication in:
* https://github.com/Cloud-CV/EvalAI/blob/master/apps/challenges/views.py#L275-L284
* https://github.com/Cloud-CV/EvalAI/blob/master/apps/participants/views.py#L230-L240
#### Remove code duplication
Remove code duplication in:
* https://github.com/Cloud-CV/EvalAI/blob/master/apps/challenges/views.py#L287-L296
* https://github.com/Cloud-CV/EvalAI/blob/master/apps/participants/views.py#L243-L252
#### Remove conditional ladder from remote_submission_worker
Use common method `requests.request` 
* https://github.com/Cloud-CV/EvalAI/blob/master/scripts/workers/remote_submission_worker.py#L333-L396
Refer: https://github.com/Cloud-CV/evalai-cli/pull/237/files
#### Remove code duplication
* https://github.com/Cloud-CV/EvalAI/blob/master/apps/base/utils.py#L157-L184
* https://github.com/Cloud-CV/EvalAI/blob/master/scripts/workers/submission_worker.py#L632-L664
* https://github.com/Cloud-CV/EvalAI/blob/master/apps/jobs/sender.py#L16-L55
#### Remove code duplication
Use a common helper for achieving both
* https://github.com/Cloud-CV/EvalAI/blob/master/scripts/migration/set_team_name_unique.py#L13-L24
* https://github.com/Cloud-CV/EvalAI/blob/master/scripts/migration/set_team_name_unique.py#L28-L39
#### Remove code duplication
* https://github.com/Cloud-CV/EvalAI/blob/master/apps/jobs/views.py#L880-L889
* https://github.com/Cloud-CV/EvalAI/blob/master/apps/jobs/views.py#L1316-L1323
#### Remove code duplication
* https://github.com/Cloud-CV/EvalAI/blob/master/apps/challenges/views.py#L262-L270
* https://github.com/Cloud-CV/EvalAI/blob/master/apps/jobs/views.py#L221-L231
Note: the status codes returned are different in the above two cases for the same case (email id of a participant is banned). Consider making both same.
#### Remove code duplication
* https://github.com/Cloud-CV/EvalAI/blob/master/apps/challenges/views.py#L941-L947
* https://github.com/Cloud-CV/EvalAI/blob/master/apps/challenges/views.py#L948-L954


These changes can help code maintainability improve greatly.
Apart from this, extra refactoring can be done so as to remove
problems such as "too many return statements" or "too deeply nested statements",
many of which will be already solved by merging these changes.
