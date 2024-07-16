import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.errors import DeadlineExceeded, Flaky
from flask import Flask, session
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import logging
from app import app, get_db_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Strategies for generating test data
name_strategy = st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != "")
email_strategy = st.emails()
password_strategy = st.text(min_size=8, max_size=20)
project_name_strategy = st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != "")
project_description_strategy = st.text(min_size=1, max_size=200)
date_strategy = st.dates(min_value=datetime.now().date() + timedelta(days=1), max_value=datetime.now().date() + timedelta(days=365))
task_description_strategy = st.text(min_size=1, max_size=100).filter(lambda x: x.strip() != "")
task_status_strategy = st.sampled_from(['Todo', 'In Progress', 'Done'])
task_priority_strategy = st.sampled_from(['Low', 'Medium', 'High'])

@pytest.fixture(scope="module")
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

total_tests = 0
successful_tests = 0

@pytest.fixture(scope="module", autouse=True)
def run_around_tests():
    global total_tests, successful_tests
    total_tests = 0
    successful_tests = 0
    yield
    success_percentage = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    print(f"\nTest Success Percentage: {success_percentage:.2f}%")
    print(f"Total Examples Run: {total_tests}")
    print(f"Successful Examples: {successful_tests}")

@settings(max_examples=275, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    name=name_strategy,
    email=email_strategy,
    password=password_strategy,
    project_name=project_name_strategy,
    project_description=project_description_strategy,
    project_deadline=date_strategy,
    task_description=task_description_strategy,
    task_status=task_status_strategy,
    task_priority=task_priority_strategy,
    task_deadline=date_strategy
)
def test_project_and_task_management_flow(client, name, email, password, project_name, project_description, project_deadline,
                                          task_description, task_status, task_priority, task_deadline):
    global total_tests, successful_tests
    total_tests += 1
    success_count = 0
    total_steps = 6

    try:
        with patch('app.get_db_connection') as mock_get_db_connection, \
             patch('flask_login.utils._get_user') as mock_current_user:
            mock_cursor = MagicMock()
            mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
            mock_current_user.return_value.id = 1
            
            # Step 1: Registration
            logger.info(f"Attempting registration with email: {email}")
            response = client.post('/register', data={
                'name': name,
                'email': email,
                'password': password
            })
            if response.status_code in [200, 302]:
                success_count += 1
                logger.info("Registration successful")
            else:
                logger.info(f"Registration failed with status code {response.status_code}")

            # Step 2: Login
            logger.info(f"Attempting login with email: {email}")
            response = client.post('/login', data={
                'email': email,
                'password': password
            })
            if response.status_code in [200, 302]:
                success_count += 1
                logger.info("Login successful")
            else:
                logger.info(f"Login failed with status code {response.status_code}")

            # Step 3: Add Project
            with client.session_transaction() as sess:
                sess['user_id'] = 1

            logger.info(f"Attempting to add project: {project_name}")
            response = client.post('/add_project', data={
                'project_name': project_name,
                'project_description': project_description,
                'project_deadline': project_deadline.strftime('%Y-%m-%d')
            }, follow_redirects=True)
            
            if response.status_code == 200:
                success_count += 1
                logger.info("Project added successfully")
            else:
                logger.info(f"Add project failed with status code {response.status_code}")

            # Step 4: Add Task
            mock_cursor.fetchone.return_value = (1,)
            logger.info(f"Attempting to add task: {task_description}")
            response = client.post('/add_task', data={
                'task_description': task_description,
                'task_status': task_status,
                'task_priority': task_priority,
                'task_deadline': task_deadline.strftime('%Y-%m-%d'),
                'project_id': 1
            }, follow_redirects=True)
            if response.status_code == 200:
                success_count += 1
                logger.info("Task added successfully")
            else:
                logger.info(f"Add task failed with status code {response.status_code}")

            # Step 5: Delete Task
            mock_cursor.fetchone.side_effect = [(1,), (1,)]
            logger.info("Attempting to delete task")
            response = client.post('/delete_task/1', follow_redirects=True)
            if response.status_code == 200:
                success_count += 1
                logger.info("Task deleted successfully")
            else:
                logger.info(f"Delete task failed with status code {response.status_code}")

            # Step 6: Delete Project
            logger.info("Attempting to delete project")
            response = client.post('/delete_project/1', follow_redirects=True)
            if response.status_code == 200:
                success_count += 1
                logger.info("Project deleted successfully")
            else:
                logger.info(f"Delete project failed with status code {response.status_code}")

        if success_count == total_steps:
            successful_tests += 1
            logger.info("All steps completed successfully")
        else:
            logger.info(f"Test failed with {success_count} successful steps out of {total_steps}")

    except Exception as e:
        logger.error(f"An error occurred during the test: {str(e)}")

    # Assert at the end to make sure Hypothesis catches any failures
    assert success_count == total_steps, f"Only {success_count} out of {total_steps} steps were successful"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])