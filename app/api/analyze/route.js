import './polyfill.js';
import { NextResponse } from 'next/server';
import { PDFParse } from 'pdf-parse';
import mammoth from 'mammoth';
import { OpenAI } from 'openai';
import { GoogleGenerativeAI } from '@google/generative-ai';

// Structured System Prompt
const SYSTEM_PROMPT = `You are an expert ATS (Applicant Tracking System) specialist and executive career coach. Your task is to analyze the provided resume text against the job description text and provide structured, actionable feedback to improve the resume for this specific job.

You must respond ONLY with a single JSON object. Do not include any explanation before or after the JSON block. The JSON object must strictly match the following schema:
{
  "match_score": integer (0 to 100 representing how well the resume matches the job description),
  "summary": "string (a professional, constructive summary of the candidate's fit for the role)",
  "strengths": ["string (bullet point highlighting a key strength/relevant experience)"],
  "keyword_gap_analysis": {
    "matching_keywords": ["string (keywords or skills present in both resume and job description)"],
    "missing_keywords": ["string (important keywords or skills in the job description that are missing or weak in the resume)"]
  },
  "bullet_point_improvements": [
    {
      "original": "string (the original weak or unoptimized bullet point from the resume)",
      "improved": "string (the rewritten, highly impactful, action-oriented, and tailored bullet point using the CAR/STAR method and keywords from the job description)",
      "rationale": "string (explanation of why the improvement is better and how it aligns with the JD)"
    }
  ],
  "tailored_sections": [
    {
      "section_name": "string (name of the section, e.g., Professional Summary, Core Competencies, Projects)",
      "content": "string (rewritten section content optimized for the target job description)"
    }
  ],
  "interview_questions": [
    {
      "question": "string (a standard or technical interview question likely to be asked for this role based on the candidate's gaps or listed experience)",
      "answer_strategy": "string (brief advice on how the candidate should approach answering this question)",
      "sample_answer": "string (a high-quality sample answer tailored to the candidate's profile)"
    }
  ]
}

Ensure all keys and structures are present. Be highly constructive, critical, and objective.`;

// Mock assessment when Demo Mode is selected
function getMockAnalysis() {
  return {
    match_score: 68,
    summary: "The candidate shows strong foundational skills in Python, JavaScript, and general software development, making them a moderate fit for the position. However, to align with the 'Senior/Mid-level Backend Engineer' requirements, the resume needs to emphasize experience with backend web frameworks (such as FastAPI or Django), database optimizations, containerization (Docker), and cloud infrastructure setup (AWS). The current bullet points are also mostly task-based rather than achievement-oriented.",
    strengths: [
      "Good core foundation in Python and SQL database structures.",
      "Versatile development experience spanning both frontend (HTML, CSS, JS) and backend scripts.",
      "Relevant academic background with a B.S. in Computer Science."
    ],
    keyword_gap_analysis: {
      matching_keywords: ["Python", "JavaScript", "HTML", "CSS", "SQL", "Git", "AWS"],
      missing_keywords: ["FastAPI", "PostgreSQL", "Docker", "CI/CD", "Redis", "Kafka", "REST APIs", "GraphQL"]
    },
    bullet_point_improvements: [
      {
        original: "Worked on developing the backend API.",
        improved: "Designed and implemented 10+ scalable REST API endpoints using Python, reducing client latency by 15%.",
        rationale: "Introduced active verbs, quantified results, and highlighted API architecture alignment with backend expectations."
      },
      {
        original: "Wrote databases queries to retrieve data.",
        improved: "Optimized complex SQL queries and structured indexing patterns, improving query response speeds by 30% on PostgreSQL databases.",
        rationale: "Specified database system (PostgreSQL) and focused on performance engineering which is highly valued in backend roles."
      },
      {
        original: "Fixed bugs and helped deploy releases.",
        improved: "Streamlined git-based releases and automated deployments, decreasing deployment-related downtime by 12%.",
        rationale: "Highlights familiarity with modern devops workflow and proactive deployment responsibility instead of passive 'helping'."
      }
    ],
    tailored_sections: [
      {
        section_name: "Professional Summary",
        content: "Backend Engineer with 3+ years of experience designing API architectures, optimizing database queries, and managing cloud deployments. Proficient in Python, SQL, and Git workflows, with a proven track record of reducing latency and improving server-side performance. Seeking to leverage backend skills to build high-performance APIs at your scale."
      },
      {
        section_name: "Technical Skills (Optimized)",
        content: "Languages: Python, SQL (PostgreSQL), JavaScript, HTML/CSS\nFrameworks & Libraries: FastAPI (Familiar), REST APIs, GraphQL\nTools & DevOps: Git, Docker, AWS (EC2, RDS, Route53), CI/CD"
      }
    ],
    interview_questions: [
      {
        question: "The job description mentions FastAPI and PostgreSQL. Can you walk us through how you would optimize a slow-performing database query in a FastAPI app?",
        answer_strategy: "Explain your step-by-step optimization process: using EXPLAIN ANALYZE to identify sequential scans, adding proper indexes (B-tree, GIN), refactoring ORM queries to avoid N+1 issues, and implementing connection pooling in FastAPI using AsyncSession.",
        sample_answer: "I would start by profiling the query with PostgreSQL's 'EXPLAIN ANALYZE' to check the execution plan. If I see sequential scans on large tables, I would introduce targeted indexing. In the FastAPI application, I would verify that we are using SQLAlchemy's async connection pool to avoid blocking I/O, and refactor queries using options like 'joinedload' to eliminate N+1 select issues."
      },
      {
        question: "Describe your experience with containerization and managing Docker deployments.",
        answer_strategy: "Discuss writing a clean Dockerfile (multi-stage builds to minimize image size), managing multi-container setups via Docker Compose, and deploying them to cloud platforms (like AWS ECS or EC2).",
        sample_answer: "In my previous projects, I containerized the backend services using multi-stage Dockerfiles to build lightweight images. I configured Docker Compose for local multi-service testing (API, database, Redis cache) and pushed the tested images to AWS ECR, which were then deployed on AWS EC2 instances, ensuring identical environments between dev and prod."
      }
    ]
  };
}

export async function POST(request) {
  try {
    const formData = await request.formData();
    const file = formData.get('file');
    const jobDescription = formData.get('jobDescription');
    const provider = formData.get('provider') || 'Google Gemini';
    const clientApiKey = formData.get('apiKey');
    let resumeText = formData.get('resumeText') || '';

    // If file is uploaded, extract its text content
    if (file && file.size > 0) {
      const buffer = Buffer.from(await file.arrayBuffer());
      const filename = file.name.toLowerCase();

      if (filename.endsWith('.pdf')) {
        const parser = new PDFParse({ data: buffer });
        const parsed = await parser.getText();
        resumeText = parsed.text;
      } else if (filename.endsWith('.docx')) {
        const parsed = await mammoth.extractRawText({ buffer });
        resumeText = parsed.value;
      } else if (filename.endsWith('.txt')) {
        resumeText = buffer.toString('utf-8');
      } else {
        return NextResponse.json({ error: 'Unsupported file type. Please upload a PDF, DOCX, or TXT file.' }, { status: 400 });
      }
    }

    // Input Validation
    if (!resumeText.trim()) {
      return NextResponse.json({ error: 'Resume text or file is required.' }, { status: 400 });
    }
    if (!jobDescription || !jobDescription.trim()) {
      return NextResponse.json({ error: 'Job description is required.' }, { status: 400 });
    }

    // Trigger Demo / Simulation mode
    if (provider === 'Demo Mode' || clientApiKey === 'DEMO') {
      return NextResponse.json(getMockAnalysis());
    }

    let parsedJson = null;

    if (provider === 'Google Gemini') {
      const apiKeyToUse = clientApiKey || process.env.GEMINI_API_KEY || process.env.OPENAI_API_KEY;
      if (!apiKeyToUse) {
        return NextResponse.json({ error: 'Gemini API key is not configured.' }, { status: 401 });
      }

      const genAI = new GoogleGenerativeAI(apiKeyToUse);
      const model = genAI.getGenerativeModel({
        model: 'gemini-2.5-flash',
        generationConfig: {
          responseMimeType: 'application/json',
          temperature: 0.2,
        },
      });

      const prompt = `${SYSTEM_PROMPT}\n\n--- RESUME TEXT ---\n${resumeText}\n\n--- JOB DESCRIPTION ---\n${jobDescription}`;
      const result = await model.generateContent(prompt);
      const responseText = result.response.text();
      parsedJson = JSON.parse(responseText);

    } else if (provider === 'OpenAI') {
      const apiKeyToUse = clientApiKey || process.env.OPENAI_API_KEY;
      if (!apiKeyToUse) {
        return NextResponse.json({ error: 'OpenAI API key is not configured.' }, { status: 401 });
      }

      const openai = new OpenAI({ apiKey: apiKeyToUse });
      const response = await openai.chat.completions.create({
        model: 'gpt-4o',
        response_format: { type: 'json_object' },
        messages: [
          { role: 'system', content: SYSTEM_PROMPT },
          { role: 'user', content: `--- RESUME TEXT ---\n${resumeText}\n\n--- JOB DESCRIPTION ---\n${jobDescription}` }
        ],
        temperature: 0.2,
      });

      const responseText = response.choices[0].message.content;
      parsedJson = JSON.parse(responseText);
    } else {
      return NextResponse.json({ error: 'Invalid AI Provider specified.' }, { status: 400 });
    }

    return NextResponse.json(parsedJson);

  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json({ error: `Analysis failed: ${error.message}` }, { status: 500 });
  }
}
