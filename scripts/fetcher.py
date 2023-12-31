import requests
from structs import Problem
import abc


class Fetcher(abc.ABC):
    @abc.abstractmethod
    def fetch_problems(self) -> dict[str, Problem]:
        pass

    @abc.abstractmethod
    def fetch_problem_description(self, problem: Problem) -> str:
        pass

    @abc.abstractmethod
    def fetch_problem_category(self, problem: Problem) -> str:
        pass


class FetcherManager:
    def __init__(self):
        self._fetchers: dict[str, Fetcher] = {
            "leetcode": LeetcodeFetcher(),
        }

    def get_fetcher(self, platform: str) -> Fetcher:
        return self._fetchers[platform]


class LeetcodeFetcher(Fetcher):
    _api_url = "https://leetcode.com/api"
    _graphql_url = "https://leetcode.com/graphql"

    def fetch_problems(self) -> dict[str, Problem]:
        problems: dict[str, Problem] = {}
        payload: list[dict] = requests.get(f"{self._api_url}/problems/all/").json()[
            "stat_status_pairs"
        ]
        for problem in payload:
            problems[str(problem["stat"]["frontend_question_id"])] = Problem(
                id=problem["stat"]["frontend_question_id"],
                title=problem["stat"]["question__title"],
                slug=problem["stat"]["question__title_slug"],
                difficulty=self._difficulty_mapper(problem["difficulty"]["level"]),
                category="",
                url=f"https://leetcode.com/problems/{problem['stat']['question__title_slug']}",
                description="",
            )

        return problems

    def fetch_problem_description(self, problem: Problem) -> str:
        query = {
            "query": "query questionContent($titleSlug: String!) {\n\tquestion(titleSlug: $titleSlug) {\n\t\tcontent\n\t\tmysqlSchemas\n\t\tdataSchemas\n\t}\n}\n",
            "operationName": "questionContent",
            "variables": {"titleSlug": problem.slug},
        }
        session = {
            "LEETCODE_SESSION": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfYXV0aF91c2VyX2lkIjoiMzY2Nzg1OCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiYWYzOWU2ODQ1MTNmZmZiZmM2OTMwN2U1NGQ4ZmQ2YWZiYWI3Zjk1ZDlhYTk0M2I1MGM2OWY0NmEzMzhlMTVmMiIsImlkIjozNjY3ODU4LCJlbWFpbCI6ImRldi53aWxsaWFucy5mYXJpYUBnbWFpbC5jb20iLCJ1c2VybmFtZSI6IndsbGZhcmlhIiwidXNlcl9zbHVnIjoid2xsZmFyaWEiLCJhdmF0YXIiOiJodHRwczovL2Fzc2V0cy5sZWV0Y29kZS5jb20vdXNlcnMvYXZhdGFycy9hdmF0YXJfMTY5NjYxNzM3OC5wbmciLCJyZWZyZXNoZWRfYXQiOjE3MDI3NjE5OTAsImlwIjoiMjgwNDo0MzE6YzdjMDo4ODJjOjVjMGM6ODY5Njo3YWJjOmMzYzMiLCJpZGVudGl0eSI6IjNkODdjZjAyMjAwYjQ3YTk0Y2JiMWY2YTk3YzcwMDM3Iiwic2Vzc2lvbl9pZCI6NTE1NTE5MjAsIl9zZXNzaW9uX2V4cGlyeSI6MTIwOTYwMH0.Q3tVmGvLLPG90MyOFBaHAb06VEt-rqjZIQPyZEYhZWE;"
        }
        problem_content = requests.post(self._graphql_url, json=query, cookies=session)
        return problem_content.json()["data"]["question"]["content"]

    def fetch_problem_category(self, problem: Problem) -> str:
        query = {
            "query": "query questionTitle($titleSlug: String!) {\n\tquestion(titleSlug: $titleSlug) {\n\t\tquestionId\n\t\tquestionFrontendId\n\t\ttitle\n\t\ttitleSlug\n\t\tisPaidOnly\n\t\tdifficulty\n\t\tlikes\n\t\tdislikes\n\t\tcategoryTitle\n\t}\n}\n",
            "operationName": "questionTitle",
            "variables": {"titleSlug": problem.slug},
        }
        problem_info = requests.post(self._graphql_url, json=query)
        return problem_info.json()["data"]["question"]["categoryTitle"]

    def _difficulty_mapper(self, difficulty: int) -> str:
        difficulties = {
            1: "Easy",
            2: "Medium",
            3: "Hard",
        }

        return difficulties[difficulty]
