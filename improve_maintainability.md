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
<details>
	<summary>https://github.com/Cloud-CV/EvalAI/blob/master/apps/challenges/views.py#L275-L284</summary>
	<p>
	```python
    if len(challenge.allowed_email_domains) > 0:
        if not is_user_in_allowed_email_domains(user_email, challenge_pk):
            message = "Sorry, users with {} email domain(s) are only allowed to participate in this challenge."
            domains = ""
            for domain in challenge.allowed_email_domains:
                domains = "{}{}{}".format(domains, "/", domain)
            domains = domains[1:]
            response_data = {"error": message.format(domains)}
            return Response(
                response_data, status=status.HTTP_406_NOT_ACCEPTABLE
            )
	```
	</p>
</details>
<details>
	<summary>https://github.com/Cloud-CV/EvalAI/blob/master/apps/participants/views.py#L230-L240</summary>
	```python
            if len(challenge.allowed_email_domains) > 0:
                if not is_user_in_allowed_email_domains(email, challenge_pk):
                    message = "Sorry, users with {} email domain(s) are only allowed to participate in this challenge."
                    domains = ""
                    for domain in challenge.allowed_email_domains:
                        domains = "{}{}{}".format(domains, "/", domain)
                    domains = domains[1:]
                    response_data = {"error": message.format(domains)}
                    return Response(
                        response_data, status=status.HTTP_406_NOT_ACCEPTABLE
                    )
	```
</details>
#### Remove code duplication
Remove code duplication in:
<details>
	<summary>https://github.com/Cloud-CV/EvalAI/blob/master/apps/challenges/views.py#L287-L296</summary>
	```python
    if is_user_in_blocked_email_domains(user_email, challenge_pk):
        message = "Sorry, users with {} email domain(s) are not allowed to participate in this challenge."
        domains = ""
        for domain in challenge.blocked_email_domains:
            domains = "{}{}{}".format(domains, "/", domain)
        domains = domains[1:]
        response_data = {"error": message.format(domains)}
        return Response(
            response_data, status=status.HTTP_406_NOT_ACCEPTABLE
        )
	```
</details>
<details>
	<summary>https://github.com/Cloud-CV/EvalAI/blob/master/apps/participants/views.py#L243-L252</summary>
	```python
            if is_user_in_blocked_email_domains(email, challenge_pk):
                message = "Sorry, users with {} email domain(s) are not allowed to participate in this challenge."
                domains = ""
                for domain in challenge.blocked_email_domains:
                    domains = "{}{}{}".format(domains, "/", domain)
                domains = domains[1:]
                response_data = {"error": message.format(domains)}
                return Response(
                    response_data, status=status.HTTP_406_NOT_ACCEPTABLE
                )
	```
</details>
#### Remove conditional ladder from remote_submission_worker
Use common method `requests.request` 
<details>
	<summary>https://github.com/Cloud-CV/EvalAI/blob/master/scripts/workers/remote_submission_worker.py#L333-L396</summary>
	```python
def make_request(url, method, data=None):
    headers = get_request_headers()
    if method == "GET":
        try:
            response = requests.get(url=url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            logger.info(
                "The worker is not able to establish connection with EvalAI"
            )
            raise
        return response.json()

    elif method == "PUT":
        try:
            response = requests.put(url=url, headers=headers, data=data)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            logger.exception(
                "The worker is not able to establish connection with EvalAI due to {}"
                % (response.json())
            )
            raise
        except requests.exceptions.HTTPError:
            logger.exception(
                "The request to URL {} is failed due to {}"
                % (url, response.json())
            )
            raise
        return response.json()

    elif method == "PATCH":
        try:
            response = requests.patch(url=url, headers=headers, data=data)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            logger.info(
                "The worker is not able to establish connection with EvalAI"
            )
            raise
        except requests.exceptions.HTTPError:
            logger.info(
                "The request to URL {} is failed due to {}"
                % (url, response.json())
            )
            raise
        return response.json()

    elif method == "POST":
        try:
            response = requests.post(url=url, headers=headers, data=data)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            logger.info(
                "The worker is not able to establish connection with EvalAI"
            )
            raise
        except requests.exceptions.HTTPError:
            logger.info(
                "The request to URL {} is failed due to {}"
                % (url, response.json())
            )
            raise
        return response.json()
	```
</details>
Refer: https://github.com/Cloud-CV/evalai-cli/pull/237/files
#### Remove code duplication
<details>
	<summary>https://github.com/Cloud-CV/EvalAI/blob/master/apps/base/utils.py#L157-L184</summary>
	```python
def get_or_create_sqs_queue_object(queue_name):
    if settings.DEBUG or settings.TEST:
        queue_name = "evalai_submission_queue"
        sqs = boto3.resource(
            "sqs",
            endpoint_url=os.environ.get("AWS_SQS_ENDPOINT", "http://sqs:9324"),
            region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "x"),
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "x"),
        )
    else:
        sqs = boto3.resource(
            "sqs",
            region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        )
    # Check if the queue exists. If no, then create one
    try:
        queue = sqs.get_queue_by_name(QueueName=queue_name)
    except botocore.exceptions.ClientError as ex:
        if (
            ex.response["Error"]["Code"]
            != "AWS.SimpleQueueService.NonExistentQueue"
        ):
            logger.exception("Cannot get queue: {}".format(queue_name))
        queue = sqs.create_queue(QueueName=queue_name)
    return queue
	```
</details>
<details>
	<summary>https://github.com/Cloud-CV/EvalAI/blob/master/scripts/workers/submission_worker.py#L632-L664</summary>
	```python
def get_or_create_sqs_queue(queue_name):
    """
    Returns:
        Returns the SQS Queue object
    """
    if settings.DEBUG or settings.TEST:
        sqs = boto3.resource(
            "sqs",
            endpoint_url=os.environ.get("AWS_SQS_ENDPOINT", "http://sqs:9324"),
            region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        )
    else:
        sqs = boto3.resource(
            "sqs",
            region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        )
    if queue_name == "":
        queue_name = "evalai_submission_queue"
    # Check if the queue exists. If no, then create one
    try:
        queue = sqs.get_queue_by_name(QueueName=queue_name)
    except botocore.exceptions.ClientError as ex:
        if (
            ex.response["Error"]["Code"]
            != "AWS.SimpleQueueService.NonExistentQueue"
        ):
            logger.exception("Cannot get queue: {}".format(queue_name))
        queue = sqs.create_queue(QueueName=queue_name)
    return queue
	```
</details>
<details>
	<summary>https://github.com/Cloud-CV/EvalAI/blob/master/apps/jobs/sender.py#L16-L55</summary>
	```python
def get_or_create_sqs_queue(queue_name):
    """
    Args:
        queue_name: Name of the SQS Queue
    Returns:
        Returns the SQS Queue object
    """
    if settings.DEBUG or settings.TEST:
        sqs = boto3.resource(
            "sqs",
            endpoint_url=os.environ.get("AWS_SQS_ENDPOINT", "http://sqs:9324"),
            region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "x"),
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "x"),
        )
        # Use default queue name in dev and test environment
        queue_name = "evalai_submission_queue"
    else:
        sqs = boto3.resource(
            "sqs",
            region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        )

    if queue_name == "":
        queue_name = "evalai_submission_queue"

    # Check if the queue exists. If not, then create one.
    try:
        queue = sqs.get_queue_by_name(QueueName=queue_name)
    except botocore.exceptions.ClientError as ex:
        if (
            ex.response["Error"]["Code"]
            == "AWS.SimpleQueueService.NonExistentQueue"
        ):
            queue = sqs.create_queue(QueueName=queue_name)
        else:
            logger.exception("Cannot get or create Queue")
    return queue
	```
</details>
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
