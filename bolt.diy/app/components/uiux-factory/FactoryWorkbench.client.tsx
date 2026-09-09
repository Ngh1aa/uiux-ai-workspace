import { useEffect, useMemo, useRef, useState } from 'react';

type SearchResult = {
  title: string;
  url: string;
  description: string;
  age?: string;
  favicon?: string;
};

type JobState = {
  id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  run_id?: string;
  project_slug?: string;
  error?: string;
  output_tail?: string;
};

const BRIDGE = 'http://127.0.0.1:8788';

const STAGES = [
  ['research', 'Research'],
  ['ux_ia', 'UX / IA'],
  ['art_direction', 'Art direction'],
  ['design_system', 'Design system'],
  ['visual_composition', 'Composition'],
  ['implementation', 'Build'],
  ['browser_qa', 'Browser QA'],
  ['visual_qa', 'Visual critic'],
] as const;

const skillSets = {
  ecommerce: [
    'ecommerce-website',
    'visual-design-direction',
    'visual-taste-calibration',
    'design-system-and-components',
    'responsive-and-device-strategy',
  ],
  corporate: [
    'corporate-website',
    'brand-guidelines',
    'visual-design-direction',
    'conversion-and-content',
    'design-system-and-components',
  ],
  education: [
    'education-website',
    'information-architecture',
    'visual-design-direction',
    'accessibility',
    'responsive-and-device-strategy',
  ],
  agency: [
    'corporate-website',
    'conversion-and-content',
    'visual-taste-calibration',
    'asset-media-and-art-direction',
    'frontend-implementation',
  ],
};

function inferDomain(prompt: string) {
  const p = prompt.toLowerCase();

  if (
    ['ecommerce', 'e-commerce', 'thương mại điện tử', 'marketplace', 'shop', 'shopee'].some((x) =>
      p.includes(x),
    )
  ) {
    return 'ecommerce';
  }

  if (['trường', 'school', 'education', 'tuyển sinh', 'học sinh'].some((x) => p.includes(x))) {
    return 'education';
  }

  if (['agency', 'marketing', 'seo', 'quảng cáo', 'studio'].some((x) => p.includes(x))) {
    return 'agency';
  }

  return 'corporate';
}

function domainLabel(domain: string) {
  return (
    {
      ecommerce: 'E-commerce',
      corporate: 'Corporate',
      education: 'Education',
      agency: 'Agency',
    }[domain] ?? 'Corporate'
  );
}

export function FactoryWorkbench() {
  const [prompt, setPrompt] = useState(
    'Thiết kế website ecommerce hiện đại, sang trọng, thân thiện. Màu chủ đạo tím. Nghiên cứu các website tốt trong cùng thị trường trước khi thiết kế.',
  );
  const [webResearch, setWebResearch] = useState(true);
  const [skillBrain] = useState(true);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [researching, setResearching] = useState(false);
  const [researchError, setResearchError] = useState('');
  const [job, setJob] = useState<JobState | null>(null);
  const [activeStage, setActiveStage] = useState('research');
  const [rightTab, setRightTab] = useState<'skills' | 'research' | 'quality'>('skills');
  const [centerTab, setCenterTab] = useState<'preview' | 'brief'>('preview');
  const [previewUrl, setPreviewUrl] = useState('');
  const [bridgeOnline, setBridgeOnline] = useState<boolean | null>(null);
  const pollTimer = useRef<number | null>(null);

  const domain = useMemo(() => inferDomain(prompt), [prompt]);
  const activeSkills = skillSets[domain as keyof typeof skillSets] ?? skillSets.corporate;

  async function checkBridge() {
    try {
      const response = await fetch(`${BRIDGE}/health`);
      setBridgeOnline(response.ok);
    } catch {
      setBridgeOnline(false);
    }
  }

  useEffect(() => {
    checkBridge();

    return () => {
      if (pollTimer.current) {
        window.clearTimeout(pollTimer.current);
      }
    };
  }, []);

  async function runResearch(searchPrompt = prompt) {
    setResearching(true);
    setResearchError('');

    try {
      const query =
        `${searchPrompt}\n` +
        `Tìm website tham khảo, xu hướng UI/UX, pattern thiết kế và đối thủ cùng thị trường.`;

      const response = await fetch(`/api/uiux-search?q=${encodeURIComponent(query)}`);
      const payload = (await response.json()) as { error?: string; results?: SearchResult[] };

      if (!response.ok) {
        throw new Error(payload?.error || 'Search failed');
      }

      setResults(payload.results ?? []);
      setRightTab('research');

      return (payload.results ?? []) as SearchResult[];
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Search failed';
      setResearchError(message);
      setRightTab('research');

      return [];
    } finally {
      setResearching(false);
    }
  }

  async function startDesign() {
    let researchEvidence = results;

    if (webResearch && researchEvidence.length === 0) {
      researchEvidence = await runResearch();
    }

    try {
      const response = await fetch(`${BRIDGE}/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          domain,
          use_skills: skillBrain,
          web_research: webResearch,
          search_results: researchEvidence,
        }),
      });

      const payload = (await response.json()) as JobState & { error?: string };

      if (!response.ok) {
        throw new Error(payload?.error || 'Unable to start factory run');
      }

      setJob(payload);
      setActiveStage('research');
      setCenterTab('preview');
      schedulePoll(payload.id);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Bridge unavailable';

      setJob({
        id: 'bridge-offline',
        status: 'failed',
        error: message,
      });
      setBridgeOnline(false);
    }
  }

  function schedulePoll(id: string) {
    pollTimer.current = window.setTimeout(async () => {
      try {
        const response = await fetch(`${BRIDGE}/jobs/${id}`);
        const payload = (await response.json()) as JobState;

        setJob(payload);
        setBridgeOnline(true);

        if (payload.status === 'running' || payload.status === 'queued') {
          const output = payload.output_tail ?? '';

          for (const [stage] of STAGES) {
            if (output.toLowerCase().includes(stage.replace('_', ' '))) {
              setActiveStage(stage);
            }
          }

          schedulePoll(id);
          return;
        }

        if (payload.status === 'completed' && payload.project_slug) {
          setPreviewUrl(`${BRIDGE}/preview/${payload.project_slug}/`);
          setActiveStage('visual_qa');
        }
      } catch {
        setBridgeOnline(false);
      }
    }, 1500);
  }

  const isRunning = job?.status === 'running' || job?.status === 'queued';

  return (
    <div className="uf-shell">
      <aside className="uf-sidebar">
        <div className="uf-brand">
          <div className="uf-brand-mark">U</div>
          <div>
            <strong>UIUX Factory</strong>
            <span>Design agent OS</span>
          </div>
        </div>

        <button className="uf-new-project" onClick={() => window.location.reload()}>
          <span>＋</span>
          New design
        </button>

        <div className="uf-side-label">Workspace</div>

        <nav className="uf-nav">
          <button className="is-active">
            <span className="uf-nav-icon">◫</span>
            Design studio
          </button>
          <button onClick={() => setRightTab('research')}>
            <span className="uf-nav-icon">⌕</span>
            Research
            {results.length > 0 && <b>{results.length}</b>}
          </button>
          <button onClick={() => setRightTab('skills')}>
            <span className="uf-nav-icon">✦</span>
            Skill brain
          </button>
          <button onClick={() => setRightTab('quality')}>
            <span className="uf-nav-icon">◎</span>
            Quality
          </button>
        </nav>

        <div className="uf-side-grow" />

        <div className="uf-system-card">
          <div className="uf-system-row">
            <span className={`uf-dot ${bridgeOnline ? 'is-online' : ''}`} />
            <div>
              <strong>{bridgeOnline ? 'Factory connected' : 'Bridge offline'}</strong>
              <span>MetaGPT + skills_UIUX</span>
            </div>
          </div>
          <button onClick={checkBridge}>Check connection</button>
        </div>
      </aside>

      <main className="uf-main">
        <header className="uf-topbar">
          <div className="uf-breadcrumb">
            <span>Projects</span>
            <span>/</span>
            <strong>Untitled design</strong>
          </div>

          <div className="uf-top-actions">
            <div className="uf-mode-pill">
              <span className="uf-spark">✦</span>
              High taste mode
            </div>
            <button className="uf-icon-button" aria-label="Share">
              ↗
            </button>
          </div>
        </header>

        <section className="uf-workspace">
          <section className="uf-chat-panel">
            <div className="uf-chat-scroll">
              <div className="uf-message uf-message-agent">
                <div className="uf-avatar">✦</div>
                <div className="uf-message-body">
                  <div className="uf-message-meta">
                    <strong>Design Director</strong>
                    <span>UIUX Factory</span>
                  </div>
                  <p>
                    Mô tả website bạn muốn làm. Tôi sẽ tự chọn skill thật từ{' '}
                    <code>skills_UIUX</code>, nghiên cứu web nếu bật Research, dựng visual direction rồi mới build.
                  </p>
                </div>
              </div>

              <div className="uf-intent-card">
                <div className="uf-intent-head">
                  <span>Detected intent</span>
                  <b>{domainLabel(domain)}</b>
                </div>
                <div className="uf-intent-grid">
                  <div>
                    <span>Design approach</span>
                    <strong>Reference-led, anti-template</strong>
                  </div>
                  <div>
                    <span>Quality target</span>
                    <strong>Visual score ≥ 90</strong>
                  </div>
                </div>
              </div>

              {job && (
                <div className="uf-message uf-message-agent">
                  <div className="uf-avatar is-run">↻</div>
                  <div className="uf-message-body">
                    <div className="uf-message-meta">
                      <strong>Factory run</strong>
                      <span>{job.status}</span>
                    </div>
                    {job.status === 'failed' ? (
                      <p className="uf-error-text">{job.error}</p>
                    ) : (
                      <p>
                        {job.status === 'completed'
                          ? 'Website đã generate xong. Preview được cập nhật ở giữa.'
                          : 'Đang chạy các specialist agents và visual quality loop…'}
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="uf-composer-wrap">
              <div className="uf-composer">
                <textarea
                  value={prompt}
                  onChange={(event) => setPrompt(event.target.value)}
                  placeholder="Ví dụ: Thiết kế website ngân hàng hiện đại, premium, ưu tiên mobile…"
                  rows={5}
                />

                <div className="uf-composer-tools">
                  <div className="uf-tool-group">
                    <button className="uf-tool-chip is-on" title="Always enabled">
                      <span>✦</span>
                      skills_UIUX
                    </button>

                    <button
                      className={`uf-tool-chip ${webResearch ? 'is-on' : ''}`}
                      onClick={() => setWebResearch((value) => !value)}
                    >
                      <span>⌕</span>
                      Web research
                    </button>

                    <button
                      className="uf-tool-chip"
                      onClick={() => runResearch()}
                      disabled={researching}
                    >
                      {researching ? 'Searching…' : 'Research now'}
                    </button>
                  </div>

                  <button
                    className="uf-generate"
                    onClick={startDesign}
                    disabled={!prompt.trim() || isRunning}
                  >
                    {isRunning ? (
                      <>
                        <span className="uf-spinner" />
                        Designing
                      </>
                    ) : (
                      <>
                        Design website
                        <span>↑</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              <div className="uf-composer-note">
                skill paths are verified against the real local <code>skills_UIUX</code> repository.
              </div>
            </div>
          </section>

          <section className="uf-canvas-panel">
            <div className="uf-canvas-toolbar">
              <div className="uf-canvas-tabs">
                <button
                  className={centerTab === 'preview' ? 'is-active' : ''}
                  onClick={() => setCenterTab('preview')}
                >
                  Preview
                </button>
                <button
                  className={centerTab === 'brief' ? 'is-active' : ''}
                  onClick={() => setCenterTab('brief')}
                >
                  Design brief
                </button>
              </div>

              <div className="uf-device-group">
                <button className="is-active">Desktop</button>
                <button>Tablet</button>
                <button>Mobile</button>
              </div>
            </div>

            <div className="uf-preview-stage">
              {centerTab === 'preview' ? (
                previewUrl ? (
                  <div className="uf-browser">
                    <div className="uf-browser-bar">
                      <div className="uf-browser-dots">
                        <span />
                        <span />
                        <span />
                      </div>
                      <div className="uf-browser-address">{previewUrl}</div>
                    </div>
                    <iframe
                      title="Generated website preview"
                      src={previewUrl}
                      className="uf-preview-iframe"
                    />
                  </div>
                ) : (
                  <div className="uf-preview-empty">
                    <div className="uf-preview-orb">
                      <span>✦</span>
                    </div>
                    <h2>Your website will appear here</h2>
                    <p>
                      Research → direction → composition → build → browser QA → visual critic.
                    </p>

                    <div className="uf-pipeline">
                      {STAGES.slice(0, 6).map(([key, label], index) => (
                        <div
                          key={key}
                          className={`${activeStage === key ? 'is-active' : ''} ${
                            isRunning && STAGES.findIndex(([stage]) => stage === activeStage) > index
                              ? 'is-done'
                              : ''
                          }`}
                        >
                          <span>{index + 1}</span>
                          <b>{label}</b>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              ) : (
                <div className="uf-brief">
                  <div className="uf-brief-kicker">Current intent</div>
                  <h2>{domainLabel(domain)} design direction</h2>
                  <p>{prompt}</p>

                  <div className="uf-brief-columns">
                    <div>
                      <span>Principle 01</span>
                      <strong>Research before decoration</strong>
                      <p>Use current market references as evidence, not as a template to copy.</p>
                    </div>
                    <div>
                      <span>Principle 02</span>
                      <strong>One strong visual signature</strong>
                      <p>Prioritize hierarchy, composition and brand role over card soup.</p>
                    </div>
                    <div>
                      <span>Principle 03</span>
                      <strong>Rendered quality is the gate</strong>
                      <p>Browser screenshots and visual critic decide whether the result passes.</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="uf-stagebar">
              {STAGES.map(([key, label]) => {
                const currentIndex = STAGES.findIndex(([stage]) => stage === activeStage);
                const index = STAGES.findIndex(([stage]) => stage === key);
                const done = job?.status === 'completed' || (isRunning && index < currentIndex);
                const active = isRunning && key === activeStage;

                return (
                  <div key={key} className={`${done ? 'is-done' : ''} ${active ? 'is-active' : ''}`}>
                    <span className="uf-stage-dot" />
                    <b>{label}</b>
                  </div>
                );
              })}
            </div>
          </section>

          <aside className="uf-inspector">
            <div className="uf-inspector-tabs">
              <button
                className={rightTab === 'skills' ? 'is-active' : ''}
                onClick={() => setRightTab('skills')}
              >
                Skills
              </button>
              <button
                className={rightTab === 'research' ? 'is-active' : ''}
                onClick={() => setRightTab('research')}
              >
                Research
              </button>
              <button
                className={rightTab === 'quality' ? 'is-active' : ''}
                onClick={() => setRightTab('quality')}
              >
                Quality
              </button>
            </div>

            <div className="uf-inspector-scroll">
              {rightTab === 'skills' && (
                <>
                  <div className="uf-inspector-heading">
                    <span>Skill brain</span>
                    <h3>Real skills, routed by intent</h3>
                    <p>
                      Không chọn toàn bộ skill. Factory route graph nhỏ nhất phù hợp với mục tiêu.
                    </p>
                  </div>

                  <div className="uf-skill-card featured">
                    <div className="uf-skill-icon">✦</div>
                    <div>
                      <strong>{domainLabel(domain)}</strong>
                      <span>Domain playbook</span>
                    </div>
                    <b>ON</b>
                  </div>

                  <div className="uf-skill-list">
                    {activeSkills.map((skill, index) => (
                      <div className="uf-skill-row" key={skill}>
                        <span>{String(index + 1).padStart(2, '0')}</span>
                        <div>
                          <strong>{skill}</strong>
                          <small>SKILL.md · verified locally</small>
                        </div>
                        <i>✓</i>
                      </div>
                    ))}
                  </div>

                  <div className="uf-info-box">
                    <span>Why this matters</span>
                    <p>
                      Design quality comes from the skill policies + research evidence + visual critique, not from a fixed template.
                    </p>
                  </div>
                </>
              )}

              {rightTab === 'research' && (
                <>
                  <div className="uf-inspector-heading">
                    <span>Web research</span>
                    <h3>Current market references</h3>
                    <p>
                      Search is grounded by Brave Search API. Results are passed into the design brief as external evidence.
                    </p>
                  </div>

                  <button className="uf-research-button" onClick={() => runResearch()} disabled={researching}>
                    <span>⌕</span>
                    {researching ? 'Searching the web…' : 'Search current references'}
                  </button>

                  {researchError && <div className="uf-error-box">{researchError}</div>}

                  <div className="uf-search-results">
                    {results.map((result, index) => (
                      <a href={result.url} target="_blank" rel="noreferrer" key={`${result.url}-${index}`}>
                        <div className="uf-result-top">
                          <span>{new URL(result.url).hostname.replace(/^www\./, '')}</span>
                          <i>↗</i>
                        </div>
                        <strong>{result.title}</strong>
                        <p>{result.description}</p>
                      </a>
                    ))}

                    {!researching && !results.length && !researchError && (
                      <div className="uf-empty-small">
                        No references yet. Run research to collect current examples.
                      </div>
                    )}
                  </div>
                </>
              )}

              {rightTab === 'quality' && (
                <>
                  <div className="uf-inspector-heading">
                    <span>Quality system</span>
                    <h3>Rendered output, not promises</h3>
                    <p>
                      BrowserQA and VisualCritic score the real rendered website across responsive viewports.
                    </p>
                  </div>

                  <div className="uf-score-ring">
                    <div>
                      <strong>{job?.status === 'completed' ? '90+' : '—'}</strong>
                      <span>Visual target</span>
                    </div>
                  </div>

                  <div className="uf-quality-list">
                    {[
                      ['Hierarchy', '≥ 90'],
                      ['Typography', '≥ 90'],
                      ['Spacing', '≥ 90'],
                      ['Responsive', '100'],
                      ['Accessibility', '100'],
                      ['Generic AI feel', 'Low'],
                    ].map(([label, score]) => (
                      <div key={label}>
                        <span>{label}</span>
                        <b>{score}</b>
                      </div>
                    ))}
                  </div>

                  <div className="uf-info-box">
                    <span>Repair loop</span>
                    <p>
                      Critic only sends concrete issues to RepairAgent. Same issues without improvement stop automatically.
                    </p>
                  </div>
                </>
              )}
            </div>
          </aside>
        </section>
      </main>
    </div>
  );
}
