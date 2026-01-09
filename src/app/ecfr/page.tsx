import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import dynamic from "next/dynamic";
import EcfrMetricsClient from "@/components/Tables/ecfr-metrics-client";

export const metadata = {
  title: "eCFR Metrics",
};

export default function EcfrPage() {
  return (
    <>
      <Breadcrumb pageName="eCFR Metrics" />
      <div className="space-y-6">
        <EcfrMetricsClient />
      </div>
    </>
  );
}
