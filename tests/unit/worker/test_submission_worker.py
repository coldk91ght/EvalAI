import boto3
import mock
import os
import shutil
import tempfile

from datetime import timedelta
from moto import mock_sqs
from os.path import join
from unittest import TestCase

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from challenges.models import Challenge
from hosts.models import ChallengeHostTeam
from scripts.workers.submission_worker import (
    create_dir,
    create_dir_as_python_package,
    load_challenge_and_return_max_submissions,
    return_file_url_per_environment,
    get_or_create_sqs_queue
)


class BaseAPITestClass(TestCase):
    def setUp(self):
        self.BASE_TEMP_DIR = tempfile.mkdtemp()
        self.temp_directory = join(self.BASE_TEMP_DIR, "temp_dir")
        self.url = "/test/url"
        self.input_file = open(join(self.BASE_TEMP_DIR, 'dummy_input.txt'), "w+")
        self.input_file.write("file_content")
        self.input_file.close()
        self.sqs_client = boto3.client(
            "sqs",
            endpoint_url=os.environ.get("AWS_SQS_ENDPOINT", "http://sqs:9324"),
            region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        )
        self.user = User(
            username="someuser",
            email="user@test.com",
            password="secret_password",
        )
        self.challenge_host_team = ChallengeHostTeam(
            team_name="Test Challenge Host Team", created_by=self.user
        )
        self.challenge = Challenge(
            title="Test Challenge",
            description="Description for test challenge",
            terms_and_conditions="Terms and conditions for test challenge",
            submission_guidelines="Submission guidelines for test challenge",
            creator=self.challenge_host_team,
            start_date=timezone.now() - timedelta(days=2),
            end_date=timezone.now() + timedelta(days=1),
            published=False,
            enable_forum=True,
            anonymous_leaderboard=False,
            max_concurrent_submission_evaluation=200000,
            evaluation_script=SimpleUploadedFile(
                "test_sample_file.txt",
                b"Dummy file content",
                content_type="text/plain",
            ),
        )

    def test_create_dir(self):
        create_dir(self.temp_directory)
        self.assertTrue(os.path.isdir(self.temp_directory))
        shutil.rmtree(self.temp_directory)

    def test_create_dir_as_python_package(self):
        create_dir_as_python_package(self.temp_directory)
        self.assertTrue(os.path.isfile(join(self.temp_directory, "__init__.py")))
        shutil.rmtree(self.temp_directory)

    def test_return_file_url_per_environment(self):
        returned_url = return_file_url_per_environment(self.url)
        self.assertEqual(returned_url, "http://testserver/test/url")

    @mock.patch("scripts.workers.submission_worker.Challenge.objects.get")
    def test_load_challenge_and_return_max_submissions(self, mocked_get_challenge):
        mocked_get_challenge.return_value = self.challenge
        q_params = {"pk": 1}
        response = load_challenge_and_return_max_submissions(q_params)
        mocked_get_challenge.assert_called_with(q_params)
        self.assertEqual(response, (200000, self.challenge))

    @mock_sqs()
    def test_get_or_create_sqs_queue_for_existing_queue(self):
        self.sqs_client.create_queue(QueueName="test_queue")
        get_or_create_sqs_queue("test_queue")
        queue_url = self.sqs_client.get_queue_url(QueueName='test_queue')['QueueUrl']
        self.assertTrue(queue_url)
        self.sqs_client.delete_queue(QueueUrl=queue_url)

    @mock_sqs()
    def test_get_or_create_sqs_queue_for_non_existing_queue(self):
        get_or_create_sqs_queue("test_queue_2")
        queue_url = self.sqs_client.get_queue_url(QueueName='test_queue_2')['QueueUrl']
        self.assertTrue(queue_url)
        self.sqs_client.delete_queue(QueueUrl=queue_url)
