from tests.integration.baseTestAPI import BaseTestAPI
from dataactbroker.app import createApp
from dataactcore.interfaces.db import GlobalDB
from dataactcore.models.jobModels import Submission, Job
from dataactcore.models.userModel import User
from dataactcore.utils.statusCode import StatusCode
from datetime import datetime

class UserTests(BaseTestAPI):
    """ Test user specific functions """

    @classmethod
    def setUpClass(cls):
        """Set up class-wide resources like submissions and jobs."""
        super(UserTests, cls).setUpClass()

        with createApp().app_context():
            sess = GlobalDB.db().session

            # Add submissions to one of the users

            # Delete existing submissions for approved user
            sess.query(Submission).filter(Submission.user_id == cls.approved_user_id).delete()
            sess.commit()

            for i in range(0, 5):
                sub = Submission(user_id=cls.approved_user_id)
                sub.reporting_start_date = datetime(2015, 10, 1)
                sub.reporting_end_date = datetime(2015, 12, 31)
                sess.add(sub)
            sess.commit()

            # Add submissions for agency user
            sess.query(Submission).filter(Submission.user_id == cls.agency_user_id).delete()
            sess.commit()
            for i in range(0, 6):
                sub = Submission(user_id=cls.agency_user_id)
                sub.reporting_start_date = datetime(2015, 10, 1)
                sub.reporting_end_date = datetime(2015, 12, 31)
                sub.cgac_code = "SYS"
                sess.add(sub)
                sess.commit()
                if i == 0:
                    cls.submission_id = sub.submission_id

            # Add job to first submission
            job = Job(
                submission_id=cls.submission_id,
                job_status_id=cls.jobStatusDict['running'],
                job_type_id=cls.jobTypeDict['file_upload'],
                file_type_id=cls.fileTypeDict['appropriations']
            )
            sess.add(job)
            sess.commit()
            cls.uploadId = job.job_id

    def setUp(self):
        """Test set-up."""
        super(UserTests, self).setUp()
        self.login_admin_user()

    def test_finalize_wrong_user(self):
        """Test finalizing a job as the wrong user."""
        # Jobs were submitted with the id for "approved user," so lookup
        # as "admin user" should fail.
        self.logout()
        self.login_approved_user()
        postJson = {"upload_id": self.uploadId}
        response = self.app.post_json("/v1/finalize_job/",
            postJson, expect_errors=True, headers={"x-session-id":self.session_id})
        self.check_response(response, StatusCode.CLIENT_ERROR, "Cannot finalize a job for a different agency")
        # Give submission this user's cgac code
        with createApp().app_context():
            sess = GlobalDB.db().session
            submission = sess.query(Submission).filter(Submission.submission_id == self.submission_id).one()
            user = sess.query(User).\
                filter_by(email=self.test_users['approved_email']).\
                one()
            submission.cgac_code = user.affiliations[0].cgac.cgac_code
            sess.commit()
        response = self.app.post_json("/v1/finalize_job/",
            postJson, expect_errors=True, headers={"x-session-id": self.session_id})
        self.check_response(response, StatusCode.OK)
        self.logout()

    def test_current_user(self):
        """Test retrieving current user information."""
        response = self.app.get("/v1/current_user/", headers={"x-session-id":self.session_id})
        self.check_response(response, StatusCode.OK)
        assert response.json["name"] == "Mr. Manager"
        assert response.json["skip_guide"] == False
        assert response.json["website_admin"] == True

    def test_skip_guide(self):
        """ Set skip guide to True and check value in DB """
        self.login_approved_user()
        params = {"skip_guide": True}
        response = self.app.post_json("/v1/set_skip_guide/", params, headers={"x-session-id": self.session_id})
        self.check_response(response,StatusCode.OK, "skip_guide set successfully")
        self.assertTrue(response.json["skip_guide"])
        with createApp().app_context():
            sess = GlobalDB.db().session
            user = sess.query(User).filter(User.email == self.test_users['approved_email']).one()
        self.assertTrue(user.skip_guide)

    def test_email_users(self):
        """ Test email users """
        self.login_approved_user()
        input = {"users": [self.agency_user_id], "submission_id": self.submission_id,
                 "email_template": "review_submission"}
        response = self.app.post_json("/v1/email_users/", input, headers={"x-session-id": self.session_id})
        self.check_response(response, StatusCode.OK, "Emails successfully sent")

        # missing request params
        badInput = {"users": [self.agency_user_id]}
        response = self.app.post_json("/v1/email_users/", badInput, expect_errors=True,
                                      headers={"x-session-id": self.session_id})
        self.check_response(response, StatusCode.CLIENT_ERROR)

        # invalid submission id
        badInput = {"users": [self.agency_user_id], "submission_id": -1}
        response = self.app.post_json("/v1/email_users/", badInput, expect_errors=True,
                                      headers={"x-session-id": self.session_id})
        self.check_response(response, StatusCode.CLIENT_ERROR)

        # invalid user id
        badInput = {"users": [-1], "submission_id": self.submission_id,
                 "email_template": "review_submission"}
        response = self.app.post_json("/v1/email_users/", badInput, expect_errors=True,
                                      headers={"x-session-id": self.session_id})
        self.check_response(response, StatusCode.INTERNAL_ERROR)

        # invalid email template
        badInput = {"users": [self.agency_user_id], "submission_id": self.submission_id,
                 "email_template": "not_a_real_template"}
        response = self.app.post_json("/v1/email_users/", badInput, expect_errors=True,
                                      headers={"x-session-id": self.session_id})
        self.check_response(response, StatusCode.INTERNAL_ERROR)
