import os
import tempfile
import yaml
from unittest.mock import patch, MagicMock

from automation.ops.env_to_ansible import env_to_ansible


def test_env_to_ansible_yaml_injection():
    """
    Test that env_to_ansible safely escapes potentially dangerous YAML payloads.
    It verifies that a value containing quotes, newlines or other YAML-sensitive characters
    is safely dumped as a string rather than executed as arbitrary YAML.
    """
    # Create a mock .env file
    env_content = """
# comment
DB_HOST=127.0.0.1
DB_PASSWORD=secret" \n  hacked_key: "hacked_value
"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(env_content)
        env_path = f.name

    # We need to mock os.getcwd() so the output goes to a predictable temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mocking config object
        config = MagicMock()

        with patch('os.getcwd', return_value=temp_dir):
            env_to_ansible(config, env_path=env_path, apply=True)

            output_file = os.path.join(temp_dir, "automation", "ansible", "group_vars", "generated_from_env.yml")

            # Read the generated YAML
            assert os.path.exists(output_file)
            with open(output_file, 'r') as out_f:
                generated_yaml = out_f.read()

            # Verify the headers are there
            assert "---" in generated_yaml
            assert "# Gerado automaticamente a partir do .env" in generated_yaml

            # Parse it with yaml to ensure it's structurally valid and safe
            parsed_yaml = yaml.safe_load(generated_yaml)

            assert parsed_yaml['db_host'] == '127.0.0.1'
            # Check that the injection failed, and it's just considered as a string value for DB_PASSWORD
            assert parsed_yaml['db_password'] == 'secret'
            # Check that the hacked_key wasn't injected as a new top-level key
            assert 'hacked_key' not in parsed_yaml

    os.unlink(env_path)
