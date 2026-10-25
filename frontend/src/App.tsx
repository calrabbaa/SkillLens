import { useEffect, useState } from "react";

import {
  createJob,
  createMatch,
  getJob,
  getJobs,
  getRecommendations,
  getResume,
  getResumes,
  type JobDetail,
  type JobSummary,
  type MatchResult,
  type RecommendationResult,
  type ResumeDetail,
  type ResumeSummary,
  uploadResume,
} from "./api";


function App() {
  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [resumes, setResumes] = useState<ResumeSummary[]>([]);

  const [selectedJob, setSelectedJob] =
    useState<JobDetail | null>(null);

  const [selectedResume, setSelectedResume] =
    useState<ResumeDetail | null>(null);

  const [description, setDescription] = useState("");
  const [selectedJobId, setSelectedJobId] = useState<number | null>(
    null,
  );

  const [match, setMatch] =
    useState<MatchResult | null>(null);

  const [recommendations, setRecommendations] =
    useState<RecommendationResult | null>(null);

  const [analysisStep, setAnalysisStep] = useState("");

  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [creatingJob, setCreatingJob] = useState(false);

  const [error, setError] = useState("");


  useEffect(() => {
    async function loadInitialData() {
      try {
        setLoading(true);
        setError("");

        const [loadedJobs, loadedResumes] =
          await Promise.all([
            getJobs(),
            getResumes(),
          ]);

        setJobs(loadedJobs);
        setResumes(loadedResumes);
      } catch (error) {
        console.error(error);

        setError(
            error instanceof Error
            ? error.message
            : "Could not load SkillLens data."
        )
      } finally {
        setLoading(false);
      }
    }

    void loadInitialData();
  }, []);


async function handleCreateJob() {
  const trimmedDescription = description.trim();

  if (trimmedDescription.length < 20) {
    setError(
      "Please enter a job description with at least 20 characters."
    );
    return;
  }

  if (trimmedDescription.length > 50000) {
    setError(
      "The job description must not exceed 50,000 characters."
    );
    return;
  }

  if (creatingJob) return;

  try {
    setCreatingJob(true);
    setError("");

    const job = await createJob(trimmedDescription);

    setJobs((current) => [
      {
        id: job.id,
        created_at: job.created_at,
        skill_count: job.skills.length,
      },
      ...current,
    ]);

    setSelectedJob(job);
    setSelectedJobId(job.id);
    setDescription("");
    setMatch(null);
    setRecommendations(null);

  } catch (error) {
    console.error(error);

    setError(
      error instanceof Error
        ? error.message
        : "Could not create the job."
    );

  } finally {
    setCreatingJob(false);
  }
}


  async function handleSelectJob(jobId: number) {
    try {
      setSelectedJobId(jobId);
      setError("");
      setMatch(null);
      setRecommendations(null);

      const job = await getJob(jobId);

      setSelectedJob(job);
    } catch (error) {
      console.error(error);

      setError(
        error instanceof Error
          ? error.message
          : "Could not load the job.",
      );
    }
  }


  async function handleUpload(
    event: React.ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    try {
      setUploading(true);
      setError("");

      const resume = await uploadResume(file);

      setSelectedResume(resume);

      setResumes((current) => [
        {
          id: resume.id,
          filename: resume.filename,
          created_at: resume.created_at,
          skill_count: resume.skills.length,
        },
        ...current,
      ]);

      setMatch(null);
      setRecommendations(null);
    } catch (error) {
      console.error(error);

      setError(
        error instanceof Error
          ? error.message
          : "Could not upload the CV.",
      );
    } finally {
      setUploading(false);

      event.target.value = "";
    }
  }


  async function handleAnalyze() {
    if (!selectedJobId) {
      setError("Please select a job.");
      return;
    }

    if (!selectedResume) {
      setError("Please upload a CV.");
      return;
    }

    try {
      setAnalyzing(true);
      setError("");
      setMatch(null);
      setRecommendations(null);

      setAnalysisStep("Calculating your skill match...");

      const matchResult = await createMatch(
        selectedJobId,
        selectedResume.id,
      );

      setMatch(matchResult);

      setAnalysisStep(
        "Generating personalized skill-gap recommendations...",
      );

      const recommendationResult =
        await getRecommendations(
          selectedJobId,
          selectedResume.id,
        );

      setRecommendations(recommendationResult);
      setAnalysisStep("");
    } catch (error) {
      console.error(error);

      setError(
        error instanceof Error
          ? error.message
          : "Could not analyze the match.",
      );
    } finally {
      setAnalyzing(false);
      setAnalysisStep("");
    }
  }


  async function handleSelectResume(resumeId: number) {
  try {
    setError("");

    const resume = await getResume(resumeId);

    setSelectedResume(resume);

    setMatch(null);
    setRecommendations(null);
  } catch (error) {
    console.error(error);

    setError(
      error instanceof Error
        ? error.message
        : "Could not load the CV.",
    );
  }
}


  if (loading) {
    return (
      <div className="app">
        <p>Loading SkillLens...</p>
      </div>
    );
  }


  return (
    <div className="app">

      <header className="app-header">
        <h1>SkillLens</h1>

        <p>
          Understand how your CV matches software
          engineering roles.
        </p>
      </header>


      <main className="dashboard">

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        <section className="card">
          <h2>Your CV</h2>

          <p className="privacy-notice">
            Your CV is processed to extract relevant skills.
            Uploaded CV data is automatically deleted after
            3 days, with cleanup running daily.
            Please avoid uploading sensitive personal information.
          </p>

          <label className="upload-area">
            <input
              type="file"
              accept="application/pdf"
              onChange={handleUpload}
              disabled={uploading}
            />

            {uploading
              ? "Analyzing CV..."
              : "Upload a PDF CV"}
          </label>

          {selectedResume && (
            <div className="selected-resource">
              <div className="cv-summary">
                <div>
                  <strong>{selectedResume.filename}</strong>
                  <p className="cv-summary-subtitle">
                    Skills identified from your uploaded CV
                  </p>
                </div>

                <span className="skill-count">
                  {selectedResume.skills.length} skills
                </span>
              </div>

              <div className="cv-skills">
                {selectedResume.skills.length > 0 ? (
                  <div className="skill-badges">
                    {selectedResume.skills.map((skill) => (
                      <span
                        key={skill.name}
                        className="skill-badge optional"
                        title={skill.category}
                      >
                        {skill.name}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="empty-skills">
                    No technical skills were detected in this CV.
                  </p>
                )}
              </div>
            </div>
          )}

          {resumes.length > 0 && (
            <div className="resume-history">
              <h3>Previous CVs</h3>

              {resumes.map((resume) => (
                <button
                  key={resume.id}
                  onClick={() => handleSelectResume(resume.id)}
                  className="history-item"
                >
                  <strong>{resume.filename}</strong>
                  <span>
                    {resume.skill_count} skills
                  </span>
                </button>
              ))}
            </div>
          )}
        </section>


        <section className="card">
          <h2>Target job</h2>

          <select
            value={selectedJobId ?? ""}
            onChange={(event) => {
              const id = Number(event.target.value);

              if (id) {
                void handleSelectJob(id);
              }
            }}
          >
            <option value="">
              Select a job
            </option>

            {jobs.map((job) => (
              <option
                key={job.id}
                value={job.id}
              >
                Job #{job.id} — {job.skill_count} skills
              </option>
            ))}
          </select>


        {selectedJob && (
          <div className="job-preview">
            <h3>Job #{selectedJob.id}</h3>

            <details className="job-description">
              <summary>View job description</summary>
              <p>{selectedJob.description}</p>
            </details>

            <div className="extracted-skills">
              <h3>
                Extracted skills
                <span className="skill-count">
                  {selectedJob.skills.length}
                </span>
              </h3>

              <h4>Required skills</h4>
              <div className="skill-badges">
                {selectedJob.skills
                  .filter((skill) => skill.required)
                  .map((skill) => (
                    <span
                      key={skill.name}
                      className="skill-badge required"
                      title={skill.category}
                    >
                      {skill.name}
                    </span>
                  ))}
              </div>

              <h4>Nice to have</h4>
              <div className="skill-badges">
                {selectedJob.skills
                  .filter((skill) => !skill.required)
                  .map((skill) => (
                    <span
                      key={skill.name}
                      className="skill-badge optional"
                      title={skill.category}
                    >
                      {skill.name}
                    </span>
                  ))}
              </div>
            </div>
          </div>
        )}
        </section>


        <section className="card">
          <h2>Add a job</h2>

          <textarea
            value={description}
            onChange={(event) => {
              setDescription(event.target.value);
              setError("");
            }}
            placeholder="Paste a job description here..."
            rows={8}
          />

          <button
            className="primary-button"
            onClick={handleCreateJob}
            disabled={creatingJob}
            aria-busy={creatingJob}
          >
            {creatingJob
              ? "Extracting skills..."
              : "Save and analyze job"}
          </button>

          {creatingJob && (
          <p className="analysis-status" role="status">
            Analyzing the job description and identifying
            technical skills. This may take a moment.
          </p>
        )}

        </section>


        <section className="card analyze-card">
          <h2>Analyze your fit</h2>

          <p className="analyze-description">
            Compare your CV with the target job to discover
            matching skills, missing requirements, and
            personalized learning recommendations.
          </p>

          <button
            className="primary-button"
            onClick={handleAnalyze}
            disabled={
              analyzing ||
              creatingJob ||
              uploading ||
              !selectedJobId ||
              !selectedResume
            }
            aria-busy={analyzing}
          >
            {analyzing ? "Analyzing..." : "Analyze match"}
          </button>

          {!selectedJobId || !selectedResume ? (
            <p className="analyze-hint">
              {!selectedResume && !selectedJobId
                ? "Upload your CV and select a target job to get started."
                : !selectedResume
                  ? "Upload your CV to continue."
                  : "Select a target job to continue."}
            </p>
          ) : null}

          {analyzing && (
            <p className="analysis-status" role="status">
              {analysisStep}
            </p>
          )}
        </section>

        {match && (
          <section className="card results">

            <div className="score">
              <div
                className="score-circle"
                style={{
                  "--score": `${match.overall_score}%`,
                } as React.CSSProperties}
              >
                <div className="score-circle-inner">
                  <strong>{match.overall_score}%</strong>
                  <span>Match</span>
                </div>
              </div>
            </div>

            <div className="match-overview">
              <div className="match-stat">
                <span className="match-stat-value">
                  {match.required_matched.length}
                  <span className="match-stat-total">
                    /{match.required_matched.length + match.required_missing.length}
                  </span>
                </span>
                <span className="match-stat-label">
                  Required skills matched
                </span>
              </div>

              <div className="match-stat">
                <span className="match-stat-value">
                  {match.preferred_matched.length}
                  <span className="match-stat-total">
                    /{match.preferred_matched.length + match.preferred_missing.length}
                  </span>
                </span>
                <span className="match-stat-label">
                  Preferred skills matched
                </span>
              </div>

              <div className="match-stat">
                <span className="match-stat-value">
                  {match.required_missing.length}
                </span>
                <span className="match-stat-label">
                  Required skills to develop
                </span>
              </div>
            </div>
            <div className="match-columns">

              <div>
                <h3 className="match-section-title">
                  Required skills
                  <span className="match-section-count">
                    {match.required_matched.length + match.required_missing.length}
                  </span>
                </h3>

                {match.required_matched.map(
                  (skill) => (
                    <div
                      className="match-skill matched"
                      key={skill.name}
                    >
                      ✓ {skill.name}
                    </div>
                  ),
                )}

                {match.required_missing.map(
                  (skill) => (
                    <div
                      className="match-skill missing"
                      key={skill.name}
                    >
                      ✗ {skill.name}
                    </div>
                  ),
                )}
              </div>


              <div>
                <h3 className="match-section-title">
                  Preferred skills
                  <span className="match-section-count">
                    {match.preferred_matched.length + match.preferred_missing.length}
                  </span>
                </h3>

                {match.preferred_matched.map(
                  (skill) => (
                    <div
                      className="match-skill matched"
                      key={skill.name}
                    >
                      ✓ {skill.name}
                    </div>
                  ),
                )}

                {match.preferred_missing.map(
                  (skill) => (
                    <div
                      className="match-skill missing"
                      key={skill.name}
                    >
                      ✗ {skill.name}
                    </div>
                  ),
                )}
              </div>

            </div>


            {match.additional_resume_skills.length >
              0 && (
                <div>
                  <h3>
                    Additional CV skills
                  </h3>

                  <div className="additional-skills">
                    {match.additional_resume_skills.map(
                      (skill) => (
                        <span key={skill.name}>
                          {skill.name}
                        </span>
                      ),
                    )}
                  </div>
                </div>
              )}

          </section>
        )}


        {recommendations &&
          recommendations.recommendations.length > 0 && (
            <section className="card skill-gaps-section">
              <div className="skill-gaps-header">
                <div>
                  <h2>Your learning roadmap</h2>
                  <p>
                    Explore your skill gaps and discover practical
                    ways to improve your job readiness.
                  </p>
                </div>

                <span className="skill-count">
                  {recommendations.recommendations.length} recommendations
                </span>
              </div>

              <div className="recommendation-list">
                {recommendations.recommendations.map(
                  (recommendation, index) => (
                    <details
                      className="recommendation-card"
                      key={recommendation.skill_name}
                      open={index === 0}
                    >
                      <summary className="recommendation-header">
                        <div className="recommendation-title">
                          <span className="recommendation-number">
                            {index + 1}
                          </span>

                          <div>
                            <h3>{recommendation.skill_name}</h3>
                            <span className="recommendation-subtitle">
                              Learning recommendation
                            </span>
                          </div>
                        </div>

                        <span
                          className="recommendation-chevron"
                          aria-hidden="true"
                        >
                          ▾
                        </span>
                      </summary>

                      <div className="recommendation-content">
                        <div className="recommendation-detail">
                          <h4>Why it matters</h4>
                          <p>{recommendation.importance}</p>
                        </div>

                        <div className="recommendation-detail">
                          <h4>What to learn</h4>
                          <p>{recommendation.what_to_learn}</p>
                        </div>

                        <div className="recommendation-project">
                          <h4>Practice project</h4>
                          <p>{recommendation.practice_project}</p>
                        </div>
                      </div>
                    </details>
                  ),
                )}
              </div>
            </section>
          )}

      </main>
    </div>
  );
}


export default App;
