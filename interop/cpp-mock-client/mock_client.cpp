#include <memory>
#include <string>

#include <grpcpp/grpcpp.h>

#include "mls_client.grpc.pb.h"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;
using namespace mls_client;

static constexpr char implementation_name[] = "Mock-C++";
static constexpr std::array<uint32_t, 2> supported_ciphersuites = {0xA0A0, 0xA1A1};
static constexpr TestVectorType test_vector_type = TestVectorType::TREE_MATH;
static constexpr std::array<char, 4> test_vector = {0, 1, 2, 3};

class MLSClientImpl final : public MLSClient::Service
{
  static const std::string fixed_test_vector;

  Status Name(ServerContext* /* context */,
              const NameRequest* /* request */,
              NameResponse* reply) override
  {
    std::cout << "Got Name request" << std::endl;
    reply->set_name(implementation_name);
    return Status::OK;
  }

  Status SupportedCiphersuites(ServerContext* /* context */,
              const SupportedCiphersuitesRequest* /* request */,
              SupportedCiphersuitesResponse* reply) override
  {
    std::cout << "Got SupportedCiphersuites request" << std::endl;
    reply->clear_ciphersuites();
    for (const auto suite : supported_ciphersuites) {
      reply->add_ciphersuites(suite);
    }
    return Status::OK;
  }

  Status GenerateTestVector(ServerContext* /* context */,
              const GenerateTestVectorRequest* request,
              GenerateTestVectorResponse* reply) override
  {
    std::cout << "Got GenerateTestVector request" << std::endl;
    if (request->type() != test_vector_type) {
      reply->set_error("Incorrect test vector type");
      std::cout << "  ... error" << std::endl;
      return Status::OK;
    }

    std::cout << "  ... ok" << std::endl;
    reply->set_test_vector(fixed_test_vector);
    return Status::OK;
  }

  Status VerifyTestVector(ServerContext* /* context */,
              const VerifyTestVectorRequest* request,
              VerifyTestVectorResponse* reply) override
  {
    std::cout << "Got VerifyTestVector request" << std::endl;
    if (request->type() != test_vector_type) {
      reply->set_error("Incorrect test vector type");
      return Status::OK;
    }

    if (request->test_vector() != fixed_test_vector) {
      reply->set_error("Incorrect test vector");
      return Status::OK;
    }

    reply->set_success(true);
    return Status::OK;
  }

};

const std::string MLSClientImpl::fixed_test_vector = {test_vector.begin(), test_vector.end()};

int
main()
{
  std::string server_address("0.0.0.0:50051");
  MLSClientImpl service;

  grpc::EnableDefaultHealthCheckService(true);
  ServerBuilder builder;
  builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
  builder.RegisterService(&service);

  std::unique_ptr<Server> server(builder.BuildAndStart());
  server->Wait();

  return 0;
}
