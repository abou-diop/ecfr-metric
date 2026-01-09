import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import dayjs from "dayjs";

type MetricRow = {
  agency_slug: string;
  Title: string;
  Level: string | number;
  Date: string;
  Value: number;
};

export async function MetricTable({
  metricName = "Word count",
  level = 1,
  start_dt = "2022-01-01",
  end_dt = "2022-02-01",
}: {
  metricName?: string;
  level?: number;
  start_dt?: string;
  end_dt?: string;
}) {
  // Server component fetch to backend FastAPI endpoint. Adjust host/port if needed.
  const res = await fetch(
    `http://localhost:8000/metric_json?metric_name=${encodeURIComponent(metricName)}&level=${level}&start_dt=${start_dt}&end_dt=${end_dt}`,
    { cache: "no-store" },
  );
  const data: MetricRow[] = await res.json();

  return (
    <div className="rounded-[10px] border border-stroke bg-white p-4 shadow-1 dark:border-dark-3 dark:bg-gray-dark dark:shadow-card sm:p-7.5">
      <Table>
        <TableHeader>
          <TableRow className="border-none bg-[#F7F9FC] dark:bg-dark-2 [&>th]:py-4 [&>th]:text-base [&>th]:text-dark [&>th]:dark:text-white">
            <TableHead className="min-w-[155px] xl:pl-7.5">Agency</TableHead>
            <TableHead>Title</TableHead>
            <TableHead>Level</TableHead>
            <TableHead>Date</TableHead>
            <TableHead className="text-right xl:pr-7.5">Value</TableHead>
          </TableRow>
        </TableHeader>

        <TableBody>
          {data.map((item, index) => (
            <TableRow key={index} className="border-[#eee] dark:border-dark-3">
              <TableCell className="min-w-[155px] xl:pl-7.5">
                <h5 className="text-dark dark:text-white">{item.agency_slug}</h5>
              </TableCell>

              <TableCell>
                <p className="text-dark dark:text-white">{item.Title}</p>
              </TableCell>

              <TableCell>
                <p className="text-dark dark:text-white">{item.Level}</p>
              </TableCell>

              <TableCell>
                <p className="text-dark dark:text-white">{dayjs(item.Date).format("MMM DD, YYYY")}</p>
              </TableCell>

              <TableCell className="xl:pr-7.5">
                <div className="flex items-center justify-end gap-x-3.5">
                  <span className="text-dark dark:text-white">{item.Value}</span>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
