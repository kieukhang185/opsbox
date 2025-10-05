## SOPS

## Tools
```bash
# install age
$ sudo apt install age
$ age --version
1.1.1

# install sops
$ curl -LO https://github.com/getsops/sops/releases/download/v3.8.1/sops_3.8.1_amd64.deb
$ sudo dpkg -i sops_3.8.1_amd64.deb
$ sops --version
sops 3.8.1
```

## Setup sops
### Generate age key

```bash
# generate private key
$ age-keygen -o ops/infra/age.key
Public key: age1sp98canpfpjenw03zjf592d4lw5g763m88hkl6cvnyv665yvqyxsadwzks
# update age key in .sops.yaml with new generated

# generate public key
$ age-keygen -y ops/infra/age.key > ops/infra/age.pub

$ cat ops/secrets/dev.app.example.enc.yaml > ops/secrets/dev.app.enc.yaml

sops -e -i ops/secrets/dev.app.enc.yaml
```

## How to resolve sops error

- Error from server (BadRequest): error when creating "STDIN": Secret in version "v1" cannot be handled as a Secret: json: cannot unmarshal number into Go struct field Secret.stringData of type string

-> Check is the any the offending keys in the secret
```bash
sops -d ops/secrets/dev.app.enc.yaml \
| yq '.stringData | to_entries[] | select(.value | type != "string")'

{
  "key": "CELERY_RESULT_TTL",
  "value": 3600
}
{
  "key": "CELERY_CONCURRENCY",
  "value": 1
}
```
- The correct should be
```bash
  CELERY_RESULT_TTL: "3600"
  CELERY_CONCURRENCY: "1"
```


## How to use a new age key (in case lost the age key - private key)

```bash
# Remove current .sops.yaml on repository (remove and push commit)
rm .sops.yaml
git add .sops.yaml
git commit -m "remove broken/obsolete sops policy"
git push ...

# recreate .sops.yaml and generate new dev.app.enc.yaml with new age key
```
