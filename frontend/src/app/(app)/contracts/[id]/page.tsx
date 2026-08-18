import { notFound } from "next/navigation";
import { getContractDetail, ContractNotFoundError } from "@/lib/api/contracts";
import { ContractDetailView } from "@/components/contract/ContractDetailView";

interface ContractDetailPageProps {
  params: { id: string };
}

export default async function ContractDetailPage({ params }: ContractDetailPageProps) {
  const { id } = params;

  let contract;
  try {
    contract = await getContractDetail(id);
  } catch (err) {
    if (err instanceof ContractNotFoundError) {
      notFound();
    }
    throw err;
  }

  return <ContractDetailView contract={contract} />;
}