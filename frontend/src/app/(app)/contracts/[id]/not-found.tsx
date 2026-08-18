export default function ContractNotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <h1 className="text-xl font-semibold text-gray-900">Contract not found</h1>
      <p className="mt-2 text-gray-600">
        This contract doesn&apos;t exist, or you don&apos;t have access to it.
      </p>
    </div>
  );
}