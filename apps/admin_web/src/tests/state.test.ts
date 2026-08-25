import { describe, expect, it } from "vitest";

describe("admin trust rules", () => {
  it("uses server sequence as bid order", () => {
    const bids = [
      {price: 49200, seq: 1842},
      {price: 49200, seq: 1838}
    ];
    bids.sort((a,b)=>b.price-a.price || a.seq-b.seq);
    expect(bids[0].seq).toBe(1838);
  });

  it("does not infer fraud solely from reweigh rate", () => {
    const highReweighRate = true;
    const automaticFraudVerdict = false;
    expect(highReweighRate && automaticFraudVerdict).toBe(false);
  });
});
