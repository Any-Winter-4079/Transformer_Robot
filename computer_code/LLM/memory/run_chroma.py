import time
import chromadb

# Time taken to add documents: 1.7994940280914307 seconds
# Time taken to query documents: 0.2862389087677002 seconds

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="chromadb_collection")

# Documents source:https://thedataquarry.com/posts/vector-db-1/
start_add_time = time.time()
collection.add(
    documents=[
        """
Pros: Is designed to perform distributed indexing and search natively on multi-modal data (images, audio, text), built on top of the Lance data format, an innovative and new columnar data format for ML. Just like Chroma, LanceDB uses an embedded, serverless architecture, and is built from the ground up in Rust, so along with Qdrant, this is the only other major vector database vendor to leverage the speed 🔥, memory safety and relatively low resource utilization of Rust 🦀.

Cons: In 2023, LanceDB is a very young database, so a lot of features are under active development, and prioritization of features will be a challenge until 2024, due to a growing engineering team.

My take: I think among all the vector databases out there, LanceDB differentiates itself the most from the rest. This is mainly because it innovates on the storage layer itself (using Lance, a new, faster columnar format than parquet, that’s designed for very efficient scans), and on the infrastructure layer – by using a serverless architecture in its cloud version. As a result, a lot of infrastructure complexity is reduced, greatly increasing the developer’s freedom and ability to build semantic search applications directly connected to data lakes in a distributed manner.

Official page: lancedb.com

""",
        """
Pros: Offers a convenient Python/JavaScript interface for developers to quickly get a vector store up and running. It was the first vector database in the market to offer embedded mode by default, where the database and application layers are tightly integrated, allowing developers to quickly build, prototype and showcase their projects to the world.

Cons: Unlike the other purpose-built vendors, Chroma is largely a Python/TypeScript wrapper around an existing OLAP database (Clickhouse), and an existing open source vector search implementation (hnswlib). For now (as of June 2023), it doesn’t implement its own storage layer.

My take: The vector DB market is rapidly evolving, and Chroma seems to be inclined8 to adopt a “wait and watch” philosophy, and are among the few vendors that are aiming to provide multiple hosting options: serverless/embedded, self-hosted (client-server) and a cloud-native distributed SaaS solution, with potentially both embedded and client-server mode. As per their road map4, Chroma’s server implementation is in progress. Another interesting area of innovation that Chroma is bringing in is a means to quantify “query relevance”, that is, how close is the returned result to the input user query. Visualizing the embedding space, which is also listed in their road map, is an area of innovation that could allow the database to be used for may applications other than search. From a long term perspective, however, we’ve never yet seen an embedded database architecture be successfully monetized in the vector search space, so its evolution (alongside LanceDB, described below) will be interesting to watch!!

Official page: trychroma.com

"""
    ],
    ids=["id1", "id2"]
)
end_add_time = time.time()

start_query_time = time.time()
results = collection.query(
    query_texts=["ancient"],
    n_results=2
)
end_query_time = time.time()
print(results)
print(f"Time taken to add documents: {end_add_time - start_add_time} seconds")
print(f"Time taken to query documents: {end_query_time - start_query_time} seconds")
