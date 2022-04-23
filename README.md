<div align="center">

<img src="https://github.com/RamiAwar/pydastic/raw/main/assets/images/pydastic.png" width="200" height="200" />
<h1>Pydastic</h1>

<a href="https://pypi.org/project/pydastic" target="_blank">
    <img src="https://img.shields.io/pypi/v/pydastic?color=%2334D058&label=pypi%20package" alt="Package version">
</a>

[![build](https://github.com/RamiAwar/pydastic/actions/workflows/build.yml/badge.svg)](https://github.com/RamiAwar/pydastic/actions/workflows/build.yml)
[![Python Version](https://img.shields.io/pypi/pyversions/pydastic.svg)](https://pypi.org/project/pydastic/)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/ramiawar/pydastic/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/ramiawar/pydastic/blob/master/.pre-commit-config.yaml)
[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/ramiawar/pydastic/releases)
[![License](https://img.shields.io/github/license/ramiawar/pydastic)](https://github.com/ramiawar/pydastic/blob/master/LICENSE)
![Coverage Report](https://github.com/RamiAwar/pydastic/raw/main/assets/images/coverage.svg)

Pydastic is an elasticsearch python ORM based on Pydantic.

</div>

## 💾 Installation

Pip:
```bash
pip install pydastic
```

Poetry:
```bash
poetry add pydastic
```


## 🚀 Features
- Simple CRUD operations supported
- Dynamic index support when committing operation


## 📋 Usage

### Defining Models
```python
from pydastic import ESModel

class User(ESModel):
    name: str
    phone: Optional[str]
    last_login: datetime = Field(default_factory=datetime.now)

    class Meta:
        index = "user"
```

### Establishing Connection
An elasticsearch connection can be setup by using the `connect` function. This function adopts the same signature as the `elasticsearch.Elasticsearch` client and supports editor autocomplete.
Make sure to call this only once. No protection is put in place against multiple calls, might affect performance negatively.

```python
from pydastic import connect

connect(hosts="localhost:9200")
```

### CRUD: Create, Update
```python
# Create and save doc
user = User(name="John", age=20)
user.save(wait_for=True)
assert user.id != None

# Update doc
user.name = "Sam"
user.save(wait_for=True)
```

### CRUD: Read Document
```python
got = User.get(id=user.id)
assert got == user
```

### CRUD: Delete
```python
user = User(name="Marie")
user.save(wait_for=True)

user.delete(wait_for=True)
```

### Dynamic Index Support
Pydastic also supports dynamic index specification. The model Metaclass index definition is still mandatory, but if an index is specified when performing operations, that will be used instead.
The model Metaclass index is technically a fallback, although most users will probably be using a single index per model. For some users, multiple indices per model are needed (for example one user index per company).

```python
user = User(name="Marie")
user.save(index="my-user", wait_for=True)

user.delete(index="my-user", wait_for=True)
```

## Support Elasticsearch Versions

Part of the build flow is running the tests using elasticsearch 7.12.0 DB as well as python client, and using 8.1.2 as well (DB as well as client, as part of a build matrix).
This ensures support for multiple versions.

## 📈 Releases

None yet.

You can see the list of available releases on the [GitHub Releases](https://github.com/ramiawar/pydastic/releases) page.

We follow [Semantic Versions](https://semver.org/) specification.

We use [`Release Drafter`](https://github.com/marketplace/actions/release-drafter). As pull requests are merged, a draft release is kept up-to-date listing the changes, ready to publish when you’re ready. With the categories option, you can categorize pull requests in release notes using labels.

## 🛡 License

[![License](https://img.shields.io/github/license/ramiawar/pydastic)](https://github.com/ramiawar/pydastic/blob/master/LICENSE)

This project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/ramiawar/pydastic/blob/master/LICENSE) for more details.

## 📃 Citation

```bibtex
@misc{pydastic,
  author = {Rami Awar},
  title = {Pydastic is an elasticsearch python ORM based on Pydantic.},
  year = {2022},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/ramiawar/pydastic}}
}
```
