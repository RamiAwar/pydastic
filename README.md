<div align="center">
  
<img src="https://github.com/RamiAwar/pydastic/raw/main/assets/images/pydastic.png" width="200" height="200" />
<h1>Pydastic</h1>
 
[![build](https://github.com/RamiAwar/pydastic/actions/workflows/build.yml/badge.svg)](https://github.com/RamiAwar/pydastic/actions/workflows/build.yml)
[![Python Version](https://img.shields.io/pypi/pyversions/pydastic.svg)](https://pypi.org/project/pydastic/)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/ramiawar/pydastic/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/ramiawar/pydastic/blob/master/.pre-commit-config.yaml)
[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/ramiawar/pydastic/releases)
[![License](https://img.shields.io/github/license/ramiawar/pydastic)](https://github.com/ramiawar/pydastic/blob/master/LICENSE)
![Coverage Report](assets/images/coverage.svg)

Pydastic is an elasticsearch python ORM based on Pydantic.

</div>

## 🚀 Features

Basic feature set still in development.

### Definition
```python
class User(ESModel):
    name: str
    phone: Optional[str]
    last_login: datetime = Field(default_factory=datetime.now)

    class Meta:
        index = "user"
```

### CRUD: Save
```python
es = Elasticsearch(hosts="localhost:9200")

user = User(name="John", age=20)
user.save(es, wait_for=True)
assert user.id != None
```

### CRUD: Get
```python
got = User.get(es, id=user.id)
assert got == user
```

### CRUD: Delete
```Not yet implemented.```


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
