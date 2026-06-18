import os
import tempfile
import yaml
from unittest.mock import patch, MagicMock

from automation.ops.env_to_ansible import env_to_ansible


def test_env_to_ansible_yaml_injection():
    """
    Test that env_to_ansible safely escapes potentially dangerous YAML payloads.
    """
    env_content = """
# comment
DB_HOST=127.0.0.1
DB_PASSWORD=secret" \n  hacked_key: "hacked_value
"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(env_content)
        env_path = f.name

    config = MagicMock()
    captured_content = {}

    def fake_write_secure_file(path, content, mode):
        captured_content['content'] = content

    with patch('automation.ops.env_to_ansible.write_secure_file', side_effect=fake_write_secure_file):
        with patch('os.getcwd', return_value=os.path.dirname(env_path)):
            env_to_ansible(config, env_path=env_path, apply=True)

            generated_yaml = captured_content['content']

            assert "---" in generated_yaml
            assert "# Gerado automaticamente a partir do .env" in generated_yaml

            parsed_yaml = yaml.safe_load(generated_yaml)

            assert parsed_yaml['db_host'] == '127.0.0.1'
            assert parsed_yaml['db_password'] == 'secret'
            assert 'hacked_key' not in parsed_yaml

    os.unlink(env_path)
