import type { ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";

import { PreviewPane } from "../PreviewPane";

const mockGetPreview = vi.fn();

vi.mock("../../api/client", () => ({
  getPreview: (...args: unknown[]) => mockGetPreview(...args),
}));

const createWrapper = () => {
  const queryClient = new QueryClient();
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe("PreviewPane", () => {
  beforeEach(() => {
    mockGetPreview.mockReset();
  });

  it("renders HTML preview inside an iframe", async () => {
    mockGetPreview.mockResolvedValue({
      content: "<h1>Hola</h1>",
      contentType: "text/html; charset=utf-8",
    });

    render(<PreviewPane path="index.html" />, { wrapper: createWrapper() });

    const iframe = await waitFor(() => screen.getByTitle(/index\.html/i));
    expect(iframe).toHaveAttribute("sandbox", "allow-scripts allow-same-origin");
    expect(iframe).toHaveAttribute("srcdoc", expect.stringContaining("Hola"));
  });

  it("renders text content inside a <pre>", async () => {
    mockGetPreview.mockResolvedValue({
      content: "console.log('test')",
      contentType: "text/plain",
    });

    render(<PreviewPane path="main.js" />, { wrapper: createWrapper() });

    const pre = await screen.findByTestId("preview-plain");
    expect(pre).toHaveTextContent("console.log('test')");
  });

  it("shows fallback message when the type is unsupported", async () => {
    mockGetPreview.mockResolvedValue({
      content: "",
      contentType: "application/octet-stream",
    });

    render(<PreviewPane path="binary.bin" />, { wrapper: createWrapper() });

    const fallback = await screen.findByText(/no preview available/i);
    expect(fallback).toBeInTheDocument();
  });
});
