# Longitudinal v3 engineering pilot 001

## Purpose

This is a bounded engineering pilot of the outcome-complete v3 memory path. It
asks whether a completed Month 1 becomes usable, host-evidenced context in Month
2 while the matched control remains memory-free. Two observed months are not a
business-performance evaluation and cannot establish that memory is beneficial.

## Frozen, unscreened worlds

The three month seeds and customer-population seed were derived without creating
or inspecting any sandbox world. For each label below, take SHA-256, interpret
the first 16 hexadecimal digits as an integer, calculate its remainder modulo
900,000, and add 100,000:

- `capage-longitudinal-v3-pilot-001:month:1` -> `548484`
- `capage-longitudinal-v3-pilot-001:month:2` -> `126970`
- `capage-longitudinal-v3-pilot-001:month:3` -> `633176`
- `capage-longitudinal-v3-pilot-001:customer-population` -> `939513`

All three months are frozen now so a later continuation cannot select its third
world after seeing the first two. The initial launch, if separately authorized,
will execute only the first four unfinished cells: both arms of Months 1 and 2.

## Cost boundary

- 50 cents maximum attributable Anthropic cost per cell
- 150 cents reserved independently for each three-month arm
- 300 cents aggregate ceiling for all six possible cells
- 200 cents absolute ceiling for the first-four-cell pilot launch

These are ceilings, not expected costs and not spending authorization. Based on
the completed v2 cells, approximately one dollar is a reasonable planning
estimate for four cells, but the ceiling governs. Model usage is metered from
provider-reported tokens and automatically debited from synthetic capital.

## Engineering acceptance checks

After the first four cells:

1. exactly four unique paid-attempt records exist and no cell was retried;
2. both arms used the same frozen seed within each observed month;
3. Month 1 of each arm received no durable memory;
4. Month 2 control received no durable memory;
5. Month 2 memory received at least one evidence-cited v3 record;
6. any observed delivery dispute retains its host score and factor breakdown;
7. delivery disputes and customer payment defaults remain separately labeled;
8. satisfaction and monthly reputation change are present in memory-arm records;
9. the append-only memory chain and checkpoint invariants verify; and
10. external and synthetic model-cost accounting reconcile.

If a relevant event does not occur by chance, its event-specific check is
unobserved rather than passed or failed. The generic synthetic regression tests
remain the evidence for unobserved outcome classes.

## Launch boundary

The workflow exists before its authorization marker. It triggers only when the
exact authorization file is added to the exact launch branch with the expected
literal token. Re-running the job is disabled. A provider failure or ambiguous
attempt stops without retry. The pilot grants no network tools, real customers,
payments, contracts, credentials, or real-world authority.
