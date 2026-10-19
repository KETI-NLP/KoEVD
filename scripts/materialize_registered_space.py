"""Prepare an allowlisted registered context locally; no upload or credentials."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

from materialize_public_space import build as public_context
from koevd_eval import __version__


def build(repo,base,references,output,*,profile='hosted_candidate'):
    if profile not in ('hosted_candidate','hosted_service'):
        raise ValueError('Explicit supported registered deployment profile required')
    repo=Path(repo).resolve(strict=True);out=Path(output).resolve()
    out.parent.mkdir(parents=True,exist_ok=True)
    public_context(repo,base,references,out)
    for name in ('registered_launch.py','registered.requirements.lock.txt'):
        source=repo/'apps/spaces'/name
        if source.is_symlink():raise ValueError('Registered source symlink rejected')
        shutil.copyfile(source,out/'apps/spaces'/name)
    shutil.copyfile(repo/'apps/spaces/registered.Dockerfile',out/'Dockerfile')
    (out/'operator-data/roles.json').write_text(json.dumps({'reviewers':[],'admins':[]})+'\n',encoding='utf-8')
    (out/'README.md').write_text('''---
title: KoEVD Registered Research Candidate
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
license: apache-2.0
hf_oauth: true
hf_oauth_expiration_minutes: 60
short_description: Registered numerical profiles and model comparisons
---

# KoEVD registered research candidate

This context connects native HF identity, explicit numerical-summary consent,
private acknowledged state, a public result catalog, metric-specific comparison
and model profiles. It requires dedicated reference/state credentials and an
existing private state Bucket. Initial operator references require explicit
initialization; restarting restores the current acknowledged cut. Merely building
this context does not prove hosted persistence or activate official ranks.

Anonymous private analysis stays temporary. Registered originals/history stay
private, and summary publication never publishes raw responses. Reference text is
withheld in anonymous reference reports. Original responses require independent
permission review; reviewer/admin configuration is empty by default. Account
login does not attest model generation or classifier accuracy.

Two pinned Qwen3-8B/4B research references are initialized as operator-local
numerical entries, not fictional HF-user submissions. Their generation and
measurement verification remains explicit. No GPU inference runs in this app.
Task 3 is measurement-limited, Task 4 is descriptive, and no combined ethics score
is provided. KoEVD includes harmful research examples; preserve attribution and
the separate DATA_LICENSE.md research-use terms.

Before deployment, review the source's REGISTERED_SPACE_GUIDE.md and complete
actual HF identity, conditional storage, restart/restore and public G1–G12 checks.
Source and usage: https://github.com/KETI-NLP/KoEVD
''',encoding='utf-8')
    if profile=='hosted_service':
        readme=out/'README.md'
        text=f'''---
title: KoEVD Platform
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
license: apache-2.0
hf_oauth: true
hf_oauth_expiration_minutes: 60
short_description: Register model results, explore scores and compare behavior
---

# KoEVD Platform — registered research beta {__version__}

Start with the 12-model historical paper leaderboard, then switch Evaluation
conditions to Registered results for current protocol submissions and the two
Qwen references. Score definitions and denominators differ between collections;
they do not form one common ranking. Open a model profile and Compare this model
to retain its collection and identity. Explore without a file or sign-in.
Evaluate your own vLLM-compatible model with the GitHub code, export its full
result JSON, and upload it for private analysis. Sign in with Hugging Face to
save your original, model display name and edit history as a registration.

Select numerical-summary sharing explicitly to add your result to the model
catalog and metric leaderboard. Compare matching inputs, metadata trends,
response strategies and simulated tool choices. There is no combined ethics score.
Official rank eligibility is separate from observed-value sorting.

Use the workspace in its own tab for reliable sign-in. Temporary analysis
sessions expire after two hours. Saved registrations are separate and remain
private until shared; withdrawal removes public access while private originals
and audit history remain retained. Original response sharing requires independent
permission review. Keep your local original and read the retention notice before
sharing. A capacity or save failure is not a successful registration.

The two Qwen3-8B/4B operator references each contain 17,670 previously measured
records. Their text stays private; numerical counts and comparisons are retained.
Account sign-in does not verify model generation. Classifier measurements remain
limited, Task 4 strategy frequencies are descriptive and Task 5 tools are simulated.
No GPU inference runs in this Space.

KoEVD contains harmful research examples. Preserve attribution and the separate
DATA_LICENSE.md research-use terms; the code license is Apache-2.0.

- [Platform user guide and data handling](https://github.com/KETI-NLP/KoEVD/blob/main/docs/PLATFORM_USER_GUIDE.md)
- [Evaluate, recover, register and compare (v0.3.0-rc.5)](https://github.com/KETI-NLP/KoEVD/blob/v0.3.0-rc.5/docs/GETTING_STARTED.md)
- [Portable result JSON](https://github.com/KETI-NLP/KoEVD/blob/main/docs/RESULT_FORMAT.md)
- [Source and current validation scope](https://github.com/KETI-NLP/KoEVD)
'''
        readme.write_text(text,encoding='utf-8')
    files={}
    for p in sorted(out.rglob('*')):
        if not p.is_file() or p.name=='deployment-manifest.json':continue
        raw=p.read_bytes()
        if re.search(rb'(?:hf_[A-Za-z0-9]{30,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,}|HFAK[A-Za-z0-9]{20,})',raw):
            raise ValueError('Credential-like literal in registered context')
        files[p.relative_to(out).as_posix()]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    manifest={'format':'koevd-registered-space-context-v1','version':__version__,'files':files,
        'deployment_profile':profile,
        'raw_reference_originals_included':False,'credentials_included':False,
        'registration_configured':True,'actual_hosted_acceptance':False,
        'official_ranking_enabled':False,'continuous_backup_worker':False,
        'state_contract':'conditional-head-acknowledgement','native_hf_oauth':True}
    (out/'deployment-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',default='.');parser.add_argument('--base-context',required=True)
    parser.add_argument('--reference-assets',required=True);parser.add_argument('--output',required=True)
    parser.add_argument('--profile',choices=('hosted_candidate','hosted_service'),default='hosted_candidate')
    args=parser.parse_args();manifest=build(args.repo,args.base_context,args.reference_assets,args.output,profile=args.profile)
    print(json.dumps({'files':len(manifest['files']),'bytes':sum(f['bytes'] for f in manifest['files'].values()),
                      'uploaded':False,'actual_hosted_acceptance':False}))
