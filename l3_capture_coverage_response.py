"""Owned-fixture capability probe; not a Merge Proof evidence adapter."""
import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys
import time

REPO = 'ohcaygo-merge-proof-validation-lab/merge-proof-l3-lab-org-rules'
assert os.environ['GITHUB_REPOSITORY'] == REPO
assert os.environ['GITHUB_API_URL'] == 'https://api.github.com'
source = pathlib.Path('.l3-uploader').resolve()
sys.path.insert(0, str(source))
spec = importlib.util.spec_from_file_location('official_upload', source / 'upload_coverage.py')
uploader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(uploader)
sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
assert sha == os.environ['EXPECTED_SOURCE_SHA']
event = json.loads(pathlib.Path(os.environ['GITHUB_EVENT_PATH']).read_text())
pr = event.get('pull_request', {}).get('number')
assert os.environ['GITHUB_EVENT_NAME'] in ('push', 'pull_request')
payload = uploader.build_payload(file_path='l3-coverage.xml', language='Python', label='l3-capability-probe', commit_oid=sha, ref=os.environ['GITHUB_REF'], pr_number=str(pr) if pr else '')
args = {'repository': REPO, 'api_url': 'https://api.github.com', 'token': os.environ['GH_TOKEN']}
status, body = uploader.upload_report(payload=payload, **args)
observations = [{'operation': 'upload', 'status': status, 'body': json.loads(body)}]
report_id = uploader.handle_response(status, body)
assert report_id and re.fullmatch(r'[A-Za-z0-9-]{1,128}', str(report_id))
for _ in range(24):
    time.sleep(5)
    status, body = uploader.fetch_upload_status(coverage_report_id=str(report_id), **args)
    parsed = json.loads(body)
    observations.append({'operation': 'status', 'status': status, 'body': parsed})
    if parsed.get('processing_status') in ('succeeded', 'failed'):
        break
# Only owned synthetic source/report responses and public run identities are emitted.
# Never emit request headers, tokens, or environment contents.
print(json.dumps({'kind': 'CAPABILITY_OBSERVATION_NOT_PROOF', 'sourceSha': sha,
                  'runId': os.environ['GITHUB_RUN_ID'], 'runAttempt': os.environ['GITHUB_RUN_ATTEMPT'],
                  'workflowRef': os.environ['GITHUB_WORKFLOW_REF'], 'responses': observations}))
assert status == 200 and observations[-1]['body'].get('processing_status') == 'succeeded'
