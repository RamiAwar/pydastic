import typing as t

from elastic_transport import (
    BaseNode,
    NodeConfig,
    NodePool,
    NodeSelector,
    Serializer,
    Transport,
)
from elastic_transport.client_utils import DEFAULT, DefaultType
from elasticsearch import Elasticsearch
from elasticsearch._sync.client.utils import _TYPE_HOSTS


class PydasticClient:
    client: Elasticsearch = None

    def __getattribute__(self, __name: str) -> t.Any:
        if __name == "client" and object.__getattribute__(self, __name) is None:
            raise AttributeError("client not initialized - make sure to call Pydastic.connect()")
        return object.__getattribute__(self, __name)


_client = PydasticClient()


def connect(
    hosts: t.Optional[_TYPE_HOSTS] = None,
    *,
    cloud_id: t.Optional[str] = None,
    api_key: t.Optional[t.Union[str, t.Tuple[str, str]]] = None,
    basic_auth: t.Optional[t.Union[str, t.Tuple[str, str]]] = None,
    bearer_auth: t.Optional[str] = None,
    opaque_id: t.Optional[str] = None,
    headers: t.Union[DefaultType, t.Mapping[str, str]] = DEFAULT,
    connections_per_node: t.Union[DefaultType, int] = DEFAULT,
    http_compress: t.Union[DefaultType, bool] = DEFAULT,
    verify_certs: t.Union[DefaultType, bool] = DEFAULT,
    ca_certs: t.Union[DefaultType, str] = DEFAULT,
    client_cert: t.Union[DefaultType, str] = DEFAULT,
    client_key: t.Union[DefaultType, str] = DEFAULT,
    ssl_assert_hostname: t.Union[DefaultType, str] = DEFAULT,
    ssl_assert_fingerprint: t.Union[DefaultType, str] = DEFAULT,
    ssl_version: t.Union[DefaultType, int] = DEFAULT,
    ssl_context: t.Union[DefaultType, t.Any] = DEFAULT,
    ssl_show_warn: t.Union[DefaultType, bool] = DEFAULT,
    transport_class: t.Type[Transport] = Transport,
    request_timeout: t.Union[DefaultType, None, float] = DEFAULT,
    node_class: t.Union[DefaultType, t.Type[BaseNode]] = DEFAULT,
    node_pool_class: t.Union[DefaultType, t.Type[NodePool]] = DEFAULT,
    randomize_nodes_in_pool: t.Union[DefaultType, bool] = DEFAULT,
    node_selector_class: t.Union[DefaultType, t.Type[NodeSelector]] = DEFAULT,
    dead_node_backoff_factor: t.Union[DefaultType, float] = DEFAULT,
    max_dead_node_backoff: t.Union[DefaultType, float] = DEFAULT,
    serializer: t.Optional[Serializer] = None,
    serializers: t.Union[DefaultType, t.Mapping[str, Serializer]] = DEFAULT,
    default_mimetype: str = "application/json",
    max_retries: t.Union[DefaultType, int] = DEFAULT,
    retry_on_status: t.Union[DefaultType, int, t.Collection[int]] = DEFAULT,
    retry_on_timeout: t.Union[DefaultType, bool] = DEFAULT,
    sniff_on_start: t.Union[DefaultType, bool] = DEFAULT,
    sniff_before_requests: t.Union[DefaultType, bool] = DEFAULT,
    sniff_on_node_failure: t.Union[DefaultType, bool] = DEFAULT,
    sniff_timeout: t.Union[DefaultType, None, float] = DEFAULT,
    min_delay_between_sniffing: t.Union[DefaultType, None, float] = DEFAULT,
    sniffed_node_callback: t.Optional[t.Callable[[t.Dict[str, t.Any], NodeConfig], t.Optional[NodeConfig]]] = None,
    meta_header: t.Union[DefaultType, bool] = DEFAULT,
    timeout: t.Union[DefaultType, None, float] = DEFAULT,
    randomize_hosts: t.Union[DefaultType, bool] = DEFAULT,
    host_info_callback: t.Optional[
        t.Callable[
            [t.Dict[str, t.Any], t.Dict[str, t.Union[str, int]]],
            t.Optional[t.Dict[str, t.Union[str, int]]],
        ]
    ] = None,
    sniffer_timeout: t.Union[DefaultType, None, float] = DEFAULT,
    sniff_on_connection_fail: t.Union[DefaultType, bool] = DEFAULT,
    http_auth: t.Union[DefaultType, t.Any] = DEFAULT,
    maxsize: t.Union[DefaultType, int] = DEFAULT,
):
    _client.client = Elasticsearch(
        hosts=hosts,
        cloud_id=cloud_id,
        api_key=api_key,
        basic_auth=basic_auth,
        bearer_auth=bearer_auth,
        opaque_id=opaque_id,
        headers=headers,
        connections_per_node=connections_per_node,
        http_compress=http_compress,
        verify_certs=verify_certs,
        ca_certs=ca_certs,
        client_cert=client_cert,
        client_key=client_key,
        ssl_assert_hostname=ssl_assert_hostname,
        ssl_assert_fingerprint=ssl_assert_fingerprint,
        ssl_version=ssl_version,
        ssl_context=ssl_context,
        ssl_show_warn=ssl_show_warn,
        transport_class=transport_class,
        request_timeout=request_timeout,
        node_class=node_class,
        node_pool_class=node_pool_class,
        randomize_nodes_in_pool=randomize_nodes_in_pool,
        node_selector_class=node_selector_class,
        dead_node_backoff_factor=dead_node_backoff_factor,
        max_dead_node_backoff=max_dead_node_backoff,
        serializer=serializer,
        serializers=serializers,
        default_mimetype=default_mimetype,
        max_retries=max_retries,
        retry_on_status=retry_on_status,
        retry_on_timeout=retry_on_timeout,
        sniff_on_start=sniff_on_start,
        sniff_before_requests=sniff_before_requests,
        sniff_on_node_failure=sniff_on_node_failure,
        sniff_timeout=sniff_timeout,
        min_delay_between_sniffing=min_delay_between_sniffing,
        sniffed_node_callback=sniffed_node_callback,
        meta_header=meta_header,
        timeout=timeout,
        randomize_hosts=randomize_hosts,
        host_info_callback=host_info_callback,
        sniffer_timeout=sniffer_timeout,
        sniff_on_connection_fail=sniff_on_connection_fail,
        http_auth=http_auth,
        maxsize=maxsize,
    )
