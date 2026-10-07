const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";


export type Skill = {
  name: string;
  category: string;
  required: boolean;
};


export type JobDetail = {
  id: number;
  description: string;
  created_at: string;
  skills: Skill[];
};


export type JobSummary = {
  id: number;
  created_at: string;
  skill_count: number;
};


async function handleResponse<T>(response: Response): Promise<T> {
  if (response.ok) {
    return response.json();
  }

  let message = `Request failed with status ${response.status}`;

  try {
    const error = await response.json();

    if (error.detail) {
      message = error.detail;
    }
  } catch {
    // Keep the default error message.
  }

  throw new Error(message);
}


export async function createJob(
  description: string,
): Promise<JobDetail> {
  const response = await fetch(`${API_BASE_URL}/jobs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      description,
    }),
  });

  return handleResponse<JobDetail>(response);
}


export async function getJobs(): Promise<JobSummary[]> {
  const response = await fetch(`${API_BASE_URL}/jobs`);

  return handleResponse<JobSummary[]>(response);
}


export async function getJob(jobId: number): Promise<JobDetail> {
  const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`);

  return handleResponse<JobDetail>(response);
}


export type ResumeSkill = {
  name: string;
  category: string;
};


export type ResumeDetail = {
  id: number;
  filename: string;
  created_at: string;
  skills: ResumeSkill[];
};


export type ResumeSummary = {
  id: number;
  filename: string;
  created_at: string;
  skill_count: number;
};


export async function uploadResume(
  file: File,
): Promise<ResumeDetail> {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/resumes`, {
    method: "POST",
    body: formData,
  });

  return handleResponse<ResumeDetail>(response);
}


export async function getResumes(): Promise<ResumeSummary[]> {
  const response = await fetch(`${API_BASE_URL}/resumes`);

  return handleResponse<ResumeSummary[]>(response);
}


export async function getResume(
  resumeId: number,
): Promise<ResumeDetail> {
  const response = await fetch(
    `${API_BASE_URL}/resumes/${resumeId}`,
  );

  return handleResponse<ResumeDetail>(response);
}


export type MatchSkill = {
  name: string;
  category: string;
};


export type MatchResult = {
  job_id: number;
  resume_id: number;
  overall_score: number;

  required_matched: MatchSkill[];
  required_missing: MatchSkill[];

  preferred_matched: MatchSkill[];
  preferred_missing: MatchSkill[];

  additional_resume_skills: MatchSkill[];
};


export async function createMatch(
  jobId: number,
  resumeId: number,
): Promise<MatchResult> {
  const response = await fetch(`${API_BASE_URL}/matches`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      job_id: jobId,
      resume_id: resumeId,
    }),
  });

  return handleResponse<MatchResult>(response);
}


export type Recommendation = {
  skill_name: string;
  importance: string;
  what_to_learn: string;
  practice_project: string;
};

export type RecommendationResult = {
  recommendations: Recommendation[];
};


export async function getRecommendations(
  jobId: number,
  resumeId: number,
): Promise<RecommendationResult> {
  const response = await fetch(
    `${API_BASE_URL}/recommendations`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        job_id: jobId,
        resume_id: resumeId,
      }),
    },
  );

  return handleResponse<RecommendationResult>(response);
}
