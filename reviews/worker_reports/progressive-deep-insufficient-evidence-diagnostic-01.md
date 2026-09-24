# Progressive Deep insufficient-evidence diagnostic 01 — durable worker report

Final status: `complete_root_cause_proven`

Dominant root-cause classification: `DOSSIER_TOO_THIN`

Task: `WORKER_TASK_PROGRESSIVE_DEEP_INSUFFICIENT_EVIDENCE_DIAGNOSTIC_01.md`  
Mode: READ-ONLY DIAGNOSTIC / REPORT  
Date: 2026-09-24

## 1. Executive conclusion

The fixed production sample proves that the dominant cause of current Deep/PASS 2 `insufficient_evidence` outcomes is **under-collected accepted Dossier evidence**, not a stale/cross-release semantic-input binding, not the repaired run-start mechanism, and not a demonstrated overly conservative Deep final-decision rule.

The strongest evidence is the combination of three observations:

1. **Closed-book Deep review supports all eight incomplete outcomes.** Using only the exact pinned profile, exact candidate input and exact accepted Dossier that the production worker was authorized to use, none of the eight incomplete cases had enough candidate-specific coverage to support a trustworthy medium-confidence final fit/not-fit under the current PASS 2 contract.
2. **The accepted Dossiers stopped too early.** Every one of the eight incomplete Dossiers is `overall_strength=limited`, all are only one or two observations, five are single-source, and several cover only one narrow topic. Yet a bounded current-public-evidence check found additional exact-product, decision-relevant player evidence readily discoverable for all eight. This does not reconstruct the historical worker's exact search surface; it proves only that the accepted "evidence_stable" state was materially thinner than the publicly available evidence.
3. **The four completed controls show Deep can finalize from limited Dossiers when the evidence is actually decisive.** All four completed outcomes are `analyzed_not_fit`, and each accepted Dossier contains a direct, candidate-specific conflict with a high-weight pinned-profile negative: loss of mastery/agency to randomness, grind/repetition, opaque systems plus repeated training, or a repetitive core loop.

The sample does show an output-threshold asymmetry: `analyzed_fit` requires all five normalized numeric taste factors, while `analyzed_not_fit` requires a completed candidate-specific negative basis and evidence. But the fixed sample does **not** prove that Deep applies an unrealistically strict semantic threshold. The incomplete cases are genuinely missing material dimensions in their canonical input, and the completed controls cross the threshold for a concrete reason rather than because Deep blindly favors negative outcomes.

Recommended next change: **change Dossier evidence preparation/acceptance only**. Do not weaken Deep first.

## 2. Architecture / ownership preflight

The diagnostic preserves the accepted architecture:

- GitHub remains control-plane owner for Progressive scope/order, exact work identity, immutable profile pin, Dossier binding, run-start confirmation, validation, attempt/recovery accounting, persistence and completeness.
- Scheduled ChatGPT remains the bounded semantic data plane.
- Dossier remains a neutral evidence-preparation stage; it must not infer personal fit.
- Deep remains the personalized final semantic stage.
- No new scheduler, retry owner, recovery authority, queue, persistent semantic cache, or alternate result path is introduced.
- This task performed no production semantic execution and authorized no recovery.

Canonical files read for this diagnostic include the current PASS 2 contract/prompt, ownership contract, current work/state, exact historical work authority for the fixed sample, accepted Dossiers, submitted result/terminal artifacts, ingest receipts, the exact pinned profile, candidate context/queue identity, and the three required predecessor worker reports.

## 3. Current production facts

Current `data/production/pre_ai/progressive_pass2_work.json` projects:

- current Deep coverage target: **465**
- current normal first-pass attempted: **49**
- current authoritative completed: **4**
- completed fit: **0**
- completed not-fit: **4**
- incomplete/recovery: **45**
- waiting for Dossier: **416**

Physical `data/cache/progressive_pass2_state.json` currently contains 55 historical/current entries:

- 50 `analysis_incomplete / insufficient_evidence`
- 4 `analyzed_not_fit`
- 1 `analysis_incomplete / terminal_execution_failure`

All 13 fixed-sample families remain present in the current 465-row candidate scope. For every fixed-sample family, current `chatgpt_taste_queue.jsonl` matches state on both `candidate_context_sha256` and `taste_fingerprint`.

Common current semantic identity:

- semantic generation: `b33cc4416860bd15a37f530c9daef8fb7755ae440929f93aa915d5363e31c490`
- profile pin: `cf4a4ecf03e72d0d77c85c5e101ce4e37ab36b8547d1bcc1deada780a8df2a6c`
- pinned profile repository: `kentrap2011-hub/stopgame-ratings-data`
- pinned profile path: `gaming_taste_live.json`
- pinned profile commit: `5e06acad2a3dc410d4d74177efc69752ade45865`
- pinned profile blob: `9b9926031889dbd98ba6585c57836d52c739a0bb`
- pinned profile content SHA256: `e2d5f363778d83ec9fdd269f29744356c1b777201fb3dc0c56e898dbd99a44b4`
- pinned profile bytes: `269906`
- Dossier evidence revision: `semantic-bounded-retrieval-2026-09-23`
- Dossier evidence binding SHA256: `5ad29bc1e4df614191d380bf832f4865f9ee73bab406e314f8d5687b0daa7ec7`

The predecessor profile-handoff report proves the current immutable profile pin is the canonical personalized payload available to Deep. The predecessor deferred-run-start report proves the current v8 publication guard and exact authority confirmation. This task independently verified the fixed-sample run-start receipts below.

## 4. Fixed sample exact authority and bindings

Three exact confirmed run-start authorities cover the sample:

- `de503c4a56b74261c4e6794a05d21b9efc7255c3` -> authority `3fd6955e18170fb89aab78b881719f69c464b457`, started `2026-09-24T17:15:45Z`
- `cf7483cbbac2aa14074ed53b7701a25720eaa9fd` -> authority `c637e2dae2551ed148caeb3eac94d853f4604f02`, started `2026-09-24T18:11:37Z`
- `978b201e4bd03dd86432f19177c9e36250e99eb4` -> authority `c2cdc5ef40dc93cc19c6ef42a12afa7bb3c0cf63`, started `2026-09-24T19:07:45Z`

Every receipt is `status=confirmed`, carries the common semantic generation/profile pin above, and exactly matches the authority copied into its accepted result or terminal receipt.

| appid | role / outcome | exact work_id | candidate context SHA256 | accepted Dossier SHA256 | authorization_id | result/terminal introduction commit | canonical ingest receipt |
|---|---|---|---|---|---|---|---|
| 1227280 | control / not-fit | `3dc6069169fa5529a7ba2bd4cd4af6fb86d87bb3fcec09d122626aa153cfd243` | `574bf5ebed4ed8eae3bdf9d987c6b83d388e152def502b5ea248423c16ddcfeb` | `afef9520cb51b04144af125e85a6584d7b6add26a982650598223a4f2d080fc2` | `2a33faf5d2fd0c65ab6b87c8a1c18cdf284df71910d1b4130c4f2a1cab2b2746` | `6a1881ff28a46484c111b1896a8267d0a0c5b18d` | `3ae1846367c980c5fd2f5035d6acc1038c78fd151fe3532d31e3287605d2f795.json` |
| 1210320 | control / not-fit | `5f6db25e3f608fb1bedbe79654b506a7963e45724804678d2deff3c75b89b56f` | `6eb61f50cc14563e919dbe2b81f2bf770e4903a22de2c6a42a765869745eb4f1` | `ebdce2a50022b27d3cd63f8dd75be6cb1a3558cddc768e8a0c383370117c0dcd` | `6ba5d3afcb0daf06d55e7e8d327c4010d145e4798db6e0d7baaeaeb0fccb5884` | `4c02daccedc67f88276c831b7da1d5cf1d426482` | `eb31a06bbb902f8cbf16c55c8d304a390f7207a0dcb0ec67043144c2bb1596ab.json` |
| 1161590 | control / not-fit | `dfe774dd7ed7f98c733741cf712a6a21aaca47f7ac3dc93db4d1ec1aa01d486a` | `e54b1dfc39384dfab8fd0f10c949dfc449df2ce65b7add85204d669fad8eecde` | `ee3fe959542dd0a21eb4458deb01f5f80219b23dd953c0cba19065ff46c3fd62` | `7c808e9f538687aa61c9ca0d590396fb0876984611369f51fe40458d1066288b` | `d97404215c8561fb1efc9ccdb813ef162398edfb` | `e066265daf306baa8021b4eeb0d10267e5e23bc4c5b718a55292995965ee5614.json` |
| 1118240 | control / not-fit | `57bf13fececcbef82bf9b8360edeefce7dd6b12972331c918de933e25b4f0198` | `c5b1d8177bb40c6f54ad2c630fdbd95e96ab9df3511c76afbf86f830192850f0` | `f65d9180cbd5bdfc08d10996e33c3a1ad1bf7cbcae6ad45d150f5caa0d72eda9` | `910253f4a296c71c053b26f87b2037d1f075ae0f2d1be19f6c2ff7b9de49dec5` | `73aa0b0e22e1a99d6e668b15f3a1989e60e36d03` | `977fd5590625ee9ebf3cb04632582449c04f41854c3a0c3ad5211fabbaf77232.json` |
| 1227690 | incomplete | `6731494c282d0de9c9aa0ca398d6bf8bac310e51fae19b3bc3de172bd194bc5b` | `6bbd30cbaaaeece3955dce3d7cb9c6bd5d8cedca97a39e2da5129f993c2f4b0b` | `c9c9b73aba486c2148289de1cc3cf58c206c9afe4de0654fceb044b130b6e472` | `fbf0528532d54abb76e06b19861db94cb8808c8c2250e117d1239dc2eaf9c250` | `7267b70a623cdb360f0358dabc9e89d610ed3a50` | `95cbd73999944be84693830aef26190ee7d40a5f8c6b429c175217f6a79819fb.json` |
| 1244800 | incomplete | `eccf49c9ed210a4f2c703eeb0a232d58a9431164ebef072688c0f55377522869` | `dad1c90afd25aa3ec778267f7af067bab57f6fd88914d8fe7b2f1b5d1025b41b` | `f993aa8c6cbab18d629def73670583dd87298c32681d69862a08e2362e06020e` | `f0d4d2301e1c3be0f960d6ae43b3cbca280e5e6c8a03905bbf47ce9dd83ecebd` | `7c61eda7bc922c8276e9ddccb6513e627393c1c9` | `78a6314d1173c399c4b872d3ec36f3601310563b926d41dcf2003bb2198a4929.json` |
| 1206610 | incomplete | `f4344408bcc5d4b42903a544fc81320e2578f5407dc5a0a1a6c8ce19ba98a4b6` | `ef497801885dd0f44f416daa512865e800a1a80b7c83dc2d9e1f666a0c7c330a` | `e00885b211f795d653064a889ebe09d997fbe3f9d9bfe27bbf756fd32ca99d00` | `cf0bc18268aed184df45261ffb1fc238f09c28304811fd9db4c4ee258045e6ef` | `0c8747b7de5b0cc9952a5a3e8263f4059ec927ea` | `db32fda9dd6e96337e971fa0236f29f72d796654a0d94778c6768e21a9fa0766.json` |
| 1239690 | incomplete | `08603e36cf0d559c5dc643bb4b963c15401f0b2c2cf894ccf76504db108cae53` | `3a8bf113f96d8ebe9c69ca76cb65fc358f5dbef0bb3f32ca37369cf61654dbc3` | `3b17f8aabedf87ebea4b7e9ed08547614b25f93ccc247bc04a39635f221cb9bf` | `35aa4257cac241b0f959ee2f30562ec11c44b2daf741abc95dc3cf2ca2465224` | `db49bf6e703f7342d41371812e4cbf56e3de466c` | `c3aa0b8541246bf7b6506eebc970bee3753772eb29d2a4803820b3543d3d929b.json` |
| 1244460 | incomplete | `122321f8d8f4bb76e7e1cd2a1092d39c65e5163fef395922340e13faf97fa94d` | `c81b381e2da6b5df330ecbc37992dde09a155938190b841e11469e287bbce348` | `1fe66d55f85554d0dc00b382148a7a4e71ec2e658c145258b125f78d22bc3be1` | `1581ad19a6d9db9bb532923addc3899ce90f140deab8013a843bc3a113a36598` | `1ba5bbfe9b52e0f2c92bdc982abd4045df38341c` | `9c6255ad8046c5642315bd7bbcd103ded28c4806b36b60ccc72e65f150a0e2a2.json` |
| 1222680 | incomplete | `bc7985d2b3c059caa465b3054e6a16e0251657541b6250e5eb986dc882da2434` | `ca4cfbbcf198de9aef589f5df7d502991c570195652566ac7d9f12817d002957` | `c9296bc11f686ec19548f5dcb042994f2fe541abc68bf03ed78510b0cc5d4fa5` | `d37b30bb41bd55566f89c433c58285da0fe344c5e98dbdec9575a4281a5fc3b2` | `d96c3a539594f02596024892c04b6835f84a83d3` | `708b40458967bb34f0b9213169997d277798783d62650183b49187f810e6005e.json` |
| 1173820 | incomplete | `2e86b081e544e26b88392f4eb176e3c5bc242fdd45704a4e47d6cfe284128560` | `7e7663621bdca452fe9fa72b18b5cf532251c0430ef9d44c5dff7c2462a121a4` | `53ae7108af07b91966d0f32ef9434367cedcb918e884437b4005a7c2381b824a` | `f9d979322ab2a92b6879c3e11456cd6b677d688b6a71cfbc60890bdb504c58e9` | `92a9f5c840f3da3cac213e9671a679ceb36eb0ee` | `236c7de18fb01448ffd8f26cac70d0a17138191abe74e1eab9610cc63c88a3ef.json` |
| 1196090 | incomplete | `c65f7a5291cbae77968660e7392d993e7a723c79eb33ff7a8c8cfcd422362ef4` | `b38075bbdc52c185fbf997f0bb99addec29cac0d4424bd887361cfbf364554c3` | `e6d2d5564686b150e0da14fc69076c8af584c5fa8c835490bd0246ae2972111b` | `0f33c40e01b3c164492c9fb383a919d1a1dcd8e614a4dd7ffbdb47fc6ec1b019` | `248b7545174cfbe5c7c21d74bbfe7b328b63926f` | `7b6f62fb137760e3d5dfae81823dca2001634985e1515da487ecc4db3616d104.json` |
| 1164940 | technical control / terminal failure | `71103b6df8a6d59ba2377c28b423576250b6ae09204f34c763e0fb4897b5fb4a` | `0665d08d952f56408b70566f1bb89e3c3080b22c06845199e393ddf62b7a6a5c` | `741e7d07380969963fd9cba5a6c1fc4902d5b379058f8e870609024ec278da88` | `54304cb39478301ed526ab453034be689eaf1aeec29de304279f0bc7a1054314` | `8f7a414d388d283254fd1070a6bfc9650a764c74` | `b1e318bf2f8efedf612c57d412c700cd764535f169e41d952e3130a35efa6878.json` |

All 12 semantic result receipts above are accepted for their exact work identity. The four controls are authoritative; the eight incomplete results are accepted as non-authoritative and recovery-owned. The technical control is an accepted terminal-execution receipt, not a semantic result.

## 5. Closed-book personalized review: incomplete cases

This section intentionally uses **no current web evidence**. It uses only the exact pinned profile, the candidate semantic input, and the exact accepted Dossier bound to each result.

| appid / game | Concrete supported personalized dimensions | Material missing dimensions | Existing Dossier enough for medium-confidence final? | Production explanation detail | Closed-book classification |
|---|---|---|---|---|---|
| 1227690 / Severed Steel | Fast movement, jumping/diving/wall-running and weapon switching directly align with the profile's very strong expressive-movement signal; one late difficulty complaint is a risk, not an automatic negative. | Sustained development/variety, long-horizon repetition, control feel beyond movement description, progression, pacing and breadth. Profile explicitly forbids overfitting one strong signal such as parkour. | No. | Accepted artifact persists only `insufficient_evidence`; no detailed missing-dimension explanation is exposed. | `justified_incomplete` |
| 1244800 / Terraformers | Turn-based colony-management/card selection and balancing resources/happiness/science/terraforming establish what the core loop is. | Whether decisions deepen over time, RNG/agency quality, progression, variety, repetition, pacing, system clarity/friction and mastery payoff. | No. One descriptive anecdote is not enough for a holistic final verdict. | Bare issue code only. | `justified_incomplete` |
| 1206610 / Rubber Bandits | Chaotic play with friends is a positive shared-play signal. | The pinned profile says multiplayer itself is neutral; evidence is missing on mechanical depth, mastery, variety, repetition, progression and whether social value persists after novelty. | No. | Bare issue code only. | `justified_incomplete` |
| 1239690 / Retrowave | Simple/meditative driving plus one direct report that limited variation becomes repetitive maps to a real profile negative. | Corroboration, actual driving/control quality, progression, mode/route variety, development and whether repetition dominates the experience. | No. This is close to a negative threshold but still one anecdotal report. | Bare issue code only. | `justified_incomplete` |
| 1244460 / Jurassic World Evolution 2 | The accepted Dossier proves only a Russian localization/menu-selection fact. | Essentially all personal play dimensions: management loop, progression, mastery/agency, variety, repetition, pacing, friction, identity hooks. | No. This Dossier is not decision-ready for personalized play analysis. | Bare issue code only. | `justified_incomplete` |
| 1222680 / Need for Speed Heat | Police difficulty plus handling that improves materially with upgrades/tuning connects to known positive NFS profile signals: police escapes, racing, tuning and noticeable improvement. | Sustained driving feel, open-world activity quality, progression breadth, variety/repetition, identity and whether police difficulty is rewarding or grindy. | No. The franchise-aligned positives are meaningful but incomplete; the profile's anti-overfitting rule matters. | Bare issue code only. | `justified_incomplete` |
| 1173820 / FINAL FANTASY VI | Story/party/progression are positive candidate-specific signals; slow opening is a pacing risk. | Combat/mastery quality, encounter repetition, progression depth, variety, later pacing and longer-horizon structure. | No. | Yes. The submitted result explicitly marked controls/gameplay, repetition and mastery quality unresolved and overall evidence limited. That diagnosis matches the canonical input. | `justified_incomplete` |
| 1196090 / Scars Above | Elemental damage, weak points and mechanics-driven difficulty directly align with the pinned profile's very strong learnable-mastery signal. | Control feel, development/variety, progression, repetition, pacing, exploration structure and player-evidenced story quality. | No. | Yes. The submitted result explicitly recorded positive mastery/difficulty signals while leaving controls, variety, story evidence and pacing unresolved. That diagnosis matches the canonical input. | `justified_incomplete` |

Result: **8/8 fixed incomplete cases are justified as incomplete from their exact canonical Deep input**. The diagnostic therefore does not support `DEEP_TOO_CONSERVATIVE` as the dominant cause.

## 6. Successful-control contrast

The same closed-book standard applied to the four completed controls:

| appid / game | Accepted Dossier pattern | Why a final not-fit crossed the threshold |
|---|---|---|
| 1227280 / Despot's Game | 2 observations, 2 player-feedback records, 2 sources, Russian + non-Russian, limited strength. | Both observations hit a high-weight profile conflict: randomness can block recovery and random loot can reduce tactical agency. The pinned profile strongly values learnable mastery/agency. A completed below-threshold negative was therefore supported even without broad positive coverage. |
| 1210320 / Potion Craft | 1 observation, 3 bound records, 2 sources, Russian + non-Russian, limited strength. | The single observation is highly decision-relevant and recurrent: later progression becomes repetitive/grind-heavy after the early experimentation. Meaningless repetition without continued evolution is a strong recurring profile negative. |
| 1161590 / Punch Club 2 | 2 observations, 3 records, 2 sources, Russian + non-Russian, limited strength. | The evidence combines two strong negatives: opaque combat/progression systems and a repeated stat-training/money loop. The pinned profile dislikes unclear systems and repetition without meaningful evolution. |
| 1118240 / Lake | 1 observation, 2 records, 1 source, Russian, limited strength. | Two concrete reports describe the core mail-delivery loop itself as repetitive. This is decisive because the repetitive loop is central, not a peripheral side activity. |

The controls disprove a simpler rule such as "Deep requires multi-source evidence" or "Deep requires moderate/strong Dossier strength": Lake is single-source and every control is only `overall_strength=limited`.

What they share is **decision relevance**, not raw evidence volume. Their evidence directly resolves a major negative profile dimension strongly enough to support `completed_below_threshold`.

## 7. Dossier richness comparison

Factual Dossier shape:

| appid | outcome | observations | bound feedback records | distinct player sources | source mix | Russian status | overall strength | decision-relevant coverage |
|---|---|---:|---:|---:|---|---|---|---|
| 1227280 | not-fit | 2 | 2 | 2 | multi-source | found/used | limited | difficulty + progression/mastery agency |
| 1210320 | not-fit | 1 | 3 | 2 | multi-source | found/used | limited | repetition + late progression |
| 1161590 | not-fit | 2 | 3 | 2 | multi-source | found/used | limited | system clarity + repeated progression loop |
| 1118240 | not-fit | 1 | 2 | 1 | single-source | found/used | limited | core-loop repetition |
| 1227690 | incomplete | 2 | 2 | 1 | single-source | searched/no existence signal | limited | movement + one difficulty risk |
| 1244800 | incomplete | 1 | 1 | 1 | single-source | found/used | limited | core-loop description only |
| 1206610 | incomplete | 1 | 2 | 1 | single-source | found/used | limited | social/multiplayer enjoyment only |
| 1239690 | incomplete | 1 | 1 | 1 | single-source | found/used | limited | repetition, one anecdote |
| 1244460 | incomplete | 1 | 1 | 1 | single-source | found/used | limited | localization only |
| 1222680 | incomplete | 2 | 3 | 2 | multi-source | searched/no existence signal | limited | police difficulty + handling/tuning |
| 1173820 | incomplete | 2 | 2 | 2 | multi-source | found/used | limited | story/party/progression + early pacing |
| 1196090 | incomplete | 2 | 2 | 2 | multi-source | found/used | limited | encounter mechanics + difficulty/mastery |
| 1164940 | terminal control | 1 | 1 | 1 | single-source | found/used | limited | positive fast combat mechanics |

The important difference is not simply 1 source versus 2. Some incomplete Dossiers are multi-source; one successful control is single-source. The more predictive separator is whether the accepted observations cover a **material personalized decision dimension strongly enough to close the verdict**, versus describing only one positive, one mixed signal, or even a non-play topic while leaving the rest unresolved.

At the same time, the incomplete group is systematically thin: all are limited, none has more than two observations, and five of eight are single-source. This made the Deep stage depend on very narrow slices of the public evidence.

## 8. Bounded current-public-evidence check

This phase was run only after the eight cases were classified as under-evidenced in the closed-book review. It is **diagnostic current evidence only**. It does not claim these were the exact pages or snippets available to the historical Dossier invocation.

All eight had meaningful missing evidence readily discoverable:

1. **Severed Steel / 1227690** — current exact-product Metacritic user reviews provide additional player descriptions of the smooth wall-running/sliding/shooting loop and broader content/level experience; the exact-app Steam Community negative-review collection is also directly discoverable.  
   - https://www.metacritic.com/game/severed-steel/user-reviews/  
   - https://steamcommunity.com/app/1227690/negativereviews/?browsefilter=toprated
2. **Terraformers / 1244800** — exact-app Steam Community user reviews discuss resource/card balancing, scenario progression/difficulty and repetition/replay unlocks, adding exactly the long-horizon dimensions missing from the one-observation Dossier.  
   - https://steamcommunity.com/app/1244800/reviews/?browsefilter=toprated
3. **Rubber Bandits / 1206610** — exact-app Steam Community negative reviews explicitly report that the game can reveal most of its content quickly and become boring/repetitive, directly filling the missing sustained-variety dimension.  
   - https://steamcommunity.com/app/1206610/negativereviews/?browsefilter=toprated
4. **Retrowave / 1239690** — exact-app Steam Community review collections contain additional player feedback on repetition, modes converging on the same loop, stale scenery/limited variation and driving quality, providing corroboration and breadth beyond the single accepted anecdote.  
   - https://steamcommunity.com/app/1239690/negativereviews/?browsefilter=toprated&l=english  
   - https://steamcommunity.com/app/1239690/reviews/?browsefilter=mostrecent&p=1
5. **Jurassic World Evolution 2 / 1244460** — exact-product player feedback is readily available on Metacritic and in exact-product community discussion, including repetition/progression/replayability, while the accepted Dossier stopped with only a localization observation.  
   - https://www.metacritic.com/game/jurassic-world-evolution-2/user-reviews/?platform=pc  
   - https://www.reddit.com/r/jurassicworldevo/comments/zqfuz4/
6. **Need for Speed Heat / 1222680** — exact-product Metacritic user reviews add player evidence on customization, police/chase experience and broader driving impressions beyond the two accepted Reddit observations.  
   - https://www.metacritic.com/game/need-for-speed-heat/user-reviews/
7. **FINAL FANTASY VI Pixel Remaster / 1173820** — exact-release user reviews on GameFAQs and Metacritic contain richer player evidence on combat, character abilities, exploration, encounter frequency, progression, dungeon/side-content variety and pacing.  
   - https://gamefaqs.gamespot.com/pc/323473-final-fantasy-vi-pixel-remaster/reviews/153320  
   - https://www.metacritic.com/game/final-fantasy-vi-pixel-remaster/user-reviews/
8. **Scars Above / 1196090** — exact-product GameFAQs user review evidence directly covers controls/shooting, recycled enemies/repetitive combat, skill progression and world linearity, filling several dimensions the production result explicitly called unresolved.  
   - https://gamefaqs.gamespot.com/ps4/378383-scars-above/reviews/175278

This is not a claim that every current page would have yielded contract-valid records in the exact historical invocation. It is sufficient to prove the narrower diagnostic point: **additional exact-product, decision-relevant player evidence was reasonably discoverable and was not inherently absent from the public evidence environment**.

## 9. Dossier stop-rule finding

The active Dossier web-evidence contract says:

- prefer multiple independent player sources when practical;
- expand research when evidence is sparse;
- stop when evidence is sufficient, materially distinct required routes are exhausted, or an observed runtime/tool/liveness blocker prevents continuation;
- no finite numeric search-query/page limit is active;
- `evidence_stable` is an accepted stop reason, but boundedness is semantic/adaptive rather than a fixed one- or two-review quota.

Every fixed incomplete Dossier nevertheless has:

- `research_state=sufficient`;
- `overall_strength=limited`;
- `stop_reason=evidence_stable`.

For the fixed sample, that semantic stopping judgment is the defect. The problem is **not** that the schema permits a valid small Dossier in principle: compact evidence can be enough, as the successful controls prove. The problem is that "stable" was declared in cases where the evidence was sparse on material play dimensions and additional exact-product player evidence was readily discoverable.

The most extreme control is Jurassic World Evolution 2: the accepted Dossier's only observation is localization/menu selection. Marking that as a sufficient/stable neutral research result for a downstream personalized Deep decision is materially under-collected.

## 10. Deep sufficiency / asymmetry finding

There is a real schema asymmetry:

- `analyzed_fit` requires strong/moderate fit, medium/high confidence, candidate-specific positive evidence, and **all five normalized numeric taste factors**:
  - `gameplay_mastery`
  - `development_variety`
  - `structure_pacing_direction`
  - `identity_hooks`
  - `breadth_of_match`
- `analyzed_not_fit` requires medium/high confidence, a completed negative basis (`completed_below_threshold` or `confirmed_personal_negative`) and candidate-specific negative evidence.

That means a clear disqualifying conflict can close a not-fit without first proving every possible positive dimension. This is an intentional-looking semantic asymmetry in the current contract shape.

The fixed sample does **not** prove this asymmetry is materially too strict:

- all four successful controls contain a direct high-weight negative conflict;
- all eight incomplete cases leave material dimensions genuinely unresolved in their exact accepted Dossiers;
- Deep finalized Lake despite a single-source, limited-strength Dossier, proving it is not mechanically requiring multi-source or high recurrence;
- the two incomplete transports that expose detailed reasoning (FFVI and Scars Above) identify real missing dimensions rather than inventing an arbitrary higher threshold.

Therefore:

- threshold asymmetry: **present**
- evidence that Deep is materially over-conservative: **not proven**
- root-cause classification: **not `DEEP_TOO_CONSERVATIVE`**

After Dossier evidence preparation is repaired, Deep should be observed again before any threshold weakening is considered.

## 11. Semantic-input/profile/binding defect check

No current semantic-input or binding defect is found in the fixed sample.

Verified facts:

- all 13 are present in current candidate scope;
- all 13 queue rows match current state on candidate-context SHA and taste fingerprint;
- all fixed result/terminal artifacts carry the current semantic generation and exact profile pin;
- the exact pinned profile is fetchable at its immutable commit and is the same current pin accepted by the predecessor handoff fix;
- every sample result carries the exact Dossier SHA and compatibility binding prepared in the historical authority manifest;
- all three run-start receipts are confirmed and their authority commits match the accepted result/terminal artifacts;
- each fixed sample ingest receipt accepted the exact artifact type claimed;
- the eight incomplete outcomes are semantic `insufficient_evidence`, not Dossier freshness/binding rejection;
- no cross-release identity mismatch is present.

This closes `SEMANTIC_INPUT_OR_BINDING_DEFECT` for the fixed sample.

## 12. Technical control: Trepang2 / 1164940

Trepang2 is independent technical noise.

Its exact Dossier contains one positive Russian mechanics observation: fast/enjoyable combat with time-slowing and aggressive gunplay. But no semantic result was accepted. The exact bound artifact is a `PROGRESSIVE-PASS2-EXECUTION-RECEIPT-V1` with:

- `execution_status=executed_no_accepted_result`
- `terminal_reason=terminal_execution_failure`

The canonical ingest receipt accepted that terminal receipt and moved the item to recovery-owned state. This does not support or weaken the semantic `insufficient_evidence` diagnosis for the other eight and is correctly treated as one separate technical failure.

## 13. Dominant root-cause classification

`DOSSIER_TOO_THIN`

Why this is stronger than the alternatives:

- **not DEEP_TOO_CONSERVATIVE:** closed-book review independently agrees with 8/8 incomplete decisions; successful controls prove Deep can close on limited/single-source evidence when it is decisive.
- **not MIXED_DOSSIER_AND_DEEP:** a Deep over-conservatism defect is not proven in the fixed sample, while under-collection is directly demonstrated.
- **not SEMANTIC_INPUT_OR_BINDING_DEFECT:** exact current profile/context/Dossier/run-start/result/receipt bindings are coherent.
- **not NOT_PROVABLE:** the closed-book + control contrast + current-public discoverability evidence is sufficient to isolate the dominant failure stage.
- **terminal execution failure:** one independent technical control, not the semantic pattern.

## 14. Recommended next fix — DO NOT IMPLEMENT IN THIS TASK

Recommendation category: **change Dossier evidence preparation/acceptance**.

Smallest bounded future change:

1. Keep Dossier neutral: do not inject the user's profile or fit scoring into Dossier.
2. Tighten the existing adaptive stop rule rather than adding a fixed review/site quota.
3. Before emitting `research_state=sufficient` + `stop_reason=evidence_stable`, require the worker to perform an explicit neutral coverage check:
   - core play/mechanics must be represented when player evidence is reasonably discoverable;
   - if the current evidence is only one narrow topic (for example localization, generic social enjoyment, or a descriptive mechanic), continue through the next reasonably discoverable materially distinct player-feedback route while important ordinary play dimensions remain sparse;
   - seek decision-relevant neutral dimensions already named by the Dossier contract, especially progression/development, repetition/variety, pacing/structure, difficulty/mastery/friction and recurring positives/complaints;
   - if those dimensions cannot be obtained after the required materially distinct routes are exhausted, stop as exhausted/unresolved rather than calling sparse evidence "stable".
4. Preserve all existing privacy and exact-identity rules: exact appid/product binding, transient-author privacy, no profile-scoped persistence, no professional/editorial substitution for player feedback, Russian-attempt semantics, group atomicity and GitHub-owned control-plane/validation.
5. Do not authorize recovery from this report. Any reprocessing must come from a future GitHub-owned identity/recovery decision after an approved implementation.

Required regression cases for that future task:

- `1244460` Jurassic World Evolution 2 — localization-only evidence must not be accepted as sufficient/stable while ordinary exact-product play feedback remains readily discoverable.
- `1206610` Rubber Bandits — the Dossier must either cover sustained repetition/variety or prove applicable routes exhausted.
- `1239690` Retrowave — readily available corroborating repetition/variation evidence must not be skipped behind a one-review stable stop.
- `1244800` Terraformers — one descriptive mechanics anecdote must not terminate research before available long-horizon progression/variety evidence.
- `1173820` FINAL FANTASY VI — obvious richer player evidence on combat/progression/variety/pacing should be captured or explicitly exhausted.
- `1227690`, `1222680`, `1196090` — preserve exact-product identity while broadening material play coverage.
- successful controls `1118240` Lake and `1210320` Potion Craft — remain valid compact dossiers when the evidence is already directly decision-relevant; do **not** replace semantic sufficiency with a dumb minimum-source/review quota.

Only after those Dossier regressions pass should the next naturally authorized Deep results be used to decide whether any separate Deep threshold change is needed.

## 15. Required final analysis checklist

1. Current sample identities and exact bindings — **proven**, section 4.
2. Per-game compact comparison — **complete**, sections 5–8.
3. Successful-control evidence pattern — **proven**, section 6.
4. Incomplete-case evidence pattern — **proven**, section 5.
5. Current Dossiers materially too thin — **yes**, sections 7–9.
6. Deep semantic threshold materially too conservative — **not proven**, section 10.
7. Fit/not-fit threshold asymmetric — **yes structurally**, but sample does not prove defect, section 10.
8. Semantic-input/profile binding defect remains — **no fixed-sample defect found**, section 11.
9. One terminal failure independent technical noise — **yes**, section 12.
10. Dominant root cause — `DOSSIER_TOO_THIN`.
11. Exact next fix — **bounded Dossier evidence-preparation/acceptance stop-rule repair only; no implementation here**.

## 16. Hard-boundary attestation

This diagnostic did not:

- modify PASS 1 or PASS 2 contracts/prompts/runtime;
- modify Dossier contracts/prompts/runtime;
- authorize Deep recovery;
- reset/delete attempts, results or state;
- create replacement semantic results;
- manually process the production Deep backlog;
- run, modify, enable, disable or reschedule any Scheduled Task;
- change profile, ranking, UI or visual payload;
- turn current web research into a canonical Dossier.

Writes are limited to task/report/tracking documentation.

## 17. Final status

`complete_root_cause_proven`

Dominant root cause: `DOSSIER_TOO_THIN`.

Recommended next Director action: authorize one bounded Dossier adaptive-sufficiency/stop-rule repair with the regression set above; leave Deep decision thresholds unchanged until richer canonical Dossiers provide a fair retest.
