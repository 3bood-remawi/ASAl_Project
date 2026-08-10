import { redirect } from "next/navigation";

// The dashboard will live here later (see task 845). Until it exists,
// send people straight to the one page the app actually has.
export default function Home() {
  redirect("/upload");
}
