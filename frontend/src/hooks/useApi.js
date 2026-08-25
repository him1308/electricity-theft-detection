import { useEffect, useState } from "react";

export function useApi(loader, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    loader()
      .then((result) => mounted && setData(result))
      .catch((err) => mounted && setError(err.response?.data?.detail || err.message))
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, deps);

  return { data, loading, error, setData };
}
