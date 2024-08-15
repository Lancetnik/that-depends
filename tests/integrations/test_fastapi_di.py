import datetime
import typing

import fastapi
from starlette import status
from starlette.testclient import TestClient

from tests import container
from that_depends import container_context


async def init_di_context() -> typing.AsyncIterator[None]:
    async with container_context():
        yield


app = fastapi.FastAPI(dependencies=[fastapi.Depends(init_di_context)])


@app.get("/")
async def read_root(
    dependency: typing.Annotated[
        container.DependentFactory,
        fastapi.Depends(container.DIContainer.dependent_factory),
    ],
    free_dependency: typing.Annotated[
        container.FreeFactory,
        fastapi.Depends(container.DIContainer.resolver(container.FreeFactory)),
    ],
    singleton: typing.Annotated[
        container.SingletonFactory,
        fastapi.Depends(container.DIContainer.singleton),
    ],
) -> datetime.datetime:
    assert dependency.sync_resource == free_dependency.dependent_factory.sync_resource
    assert dependency.async_resource == free_dependency.dependent_factory.async_resource
    assert singleton.dep1
    return dependency.async_resource


client = TestClient(app)


async def test_read_main() -> None:
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert (
        datetime.datetime.fromisoformat(response.json().replace("Z", "+00:00"))
        == await container.DIContainer.async_resource()
    )
