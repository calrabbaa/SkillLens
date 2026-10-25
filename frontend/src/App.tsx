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
        setError("Could not load SkillLens data.");
      } finally {
        setLoading(false);
      }
    }

    void loadInitialData();
  }, []);


  async function handleCreateJob() {
    if (!description.trim()) {
      setError("Please enter a job description.");
      return;
    }

    try {
      setError("");

      const job = await createJob(description);

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
          : "Could not create the job.",
      );
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

        <section className="card">
          <h2>Your CV</h2>

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
              <strong>
                {selectedResume.filename}
              </strong>

              <span>
                {selectedResume.skills.length} skills detected
              </span>
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
              <h3>
                Job #{selectedJob.id}
              </h3>

              <p>
                {selectedJob.description}
              </p>
            </div>
          )}
        </section>


        <section className="card">
          <h2>Add a job</h2>

          <textarea
            value={description}
            onChange={(event) =>
              setDescription(event.target.value)
            }
            placeholder="Paste a job description here..."
            rows={8}
          />

          <button
            className="primary-button"
            onClick={handleCreateJob}
          >
            Save and analyze job
          </button>
        </section>


        <section className="card analyze-card">

          <h2>Analyze your fit</h2>

          <button
            className="primary-button"
            onClick={handleAnalyze}
            disabled={analyzing}
          >
            {analyzing
              ? "Analyzing..."
              : "Analyze match"}
            {analyzing && (
            <p className="analysis-status">
                {analysisStep}
            </p>
            )}
          </button>

        </section>


        {error && (
          <div className="error">
            {error}
          </div>
        )}


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


            <div className="match-columns">

              <div>
                <h3>Required skills</h3>

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
                <h3>Preferred skills</h3>

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
          recommendations.recommendations.length >
            0 && (
            <section className="card">

              <h2>Skill gaps</h2>

              <div className="recommendations">

                {recommendations.recommendations.map(
                  (recommendation) => (
                    <article
                      className="recommendation"
                      key={recommendation.skill_name}
                    >
                      <h3>
                        {recommendation.skill_name}
                      </h3>

                      <p>
                        <strong>
                          Why it matters
                        </strong>
                        <br />
                        {recommendation.importance}
                      </p>

                      <p>
                        <strong>
                          What to learn
                        </strong>
                        <br />
                        {recommendation.what_to_learn}
                      </p>

                      <p>
                        <strong>
                          Practice project
                        </strong>
                        <br />
                        {recommendation.practice_project}
                      </p>
                    </article>
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
