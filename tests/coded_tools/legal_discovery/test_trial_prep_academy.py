import unittest
from flask import Flask

from apps.legal_discovery.database import db
from apps.legal_discovery.trial_prep_routes import trial_prep_bp
from apps.legal_discovery.trial_prep import LessonBuilder, ResourceManager


class TrialPrepAcademyAPITest(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.init_app(app)
        app.register_blueprint(trial_prep_bp)
        self.app = app
        with app.app_context():
            db.create_all()
            manager = ResourceManager()
            resource = manager.add_manual_resource(
                "Rule 403", "http://example.com/rule403", "CA", "Rule 403 excludes relevant evidence on grounds." )
            builder = LessonBuilder()
            builder.build_from_resource(resource, topic="Evidence")
        self.client = app.test_client()

    def test_search_and_get_resource(self):
        resp = self.client.get("/api/resources/search?query=Rule")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data)
        res_id = data[0]["id"]
        resp = self.client.get(f"/api/resources/{res_id}")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("content", resp.get_json())

    def test_lesson_progress(self):
        resp = self.client.get("/api/lessons")
        self.assertEqual(resp.status_code, 200)
        lessons = resp.get_json()
        self.assertEqual(len(lessons), 1)
        lesson_id = lessons[0]["id"]
        resp = self.client.post(
            f"/api/lessons/{lesson_id}/progress",
            json={"completed": True, "quiz_score": 0.9, "thumbs_up": True},
        )
        self.assertEqual(resp.status_code, 200)
        progress = resp.get_json()
        self.assertTrue(progress["completed"])
        self.assertAlmostEqual(progress["quiz_score"], 0.9)


if __name__ == "__main__":
    unittest.main()
