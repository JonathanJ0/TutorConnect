const API_BASE_URL = 'http://localhost:5000/api';

export interface Session {
  id: number;
  tutor: string;
  learner: string;
  subject: string;
  payment: number;
  completed: boolean;
}

export interface Quiz {
  questions: Array<{
    question: string;
    answer: string;
    options: string[];
  }>;
}

export const api = {
  // Sessions
  getSessions: async (): Promise<Session[]> => {
    const response = await fetch(`${API_BASE_URL}/sessions`);
    if (!response.ok) throw new Error('Failed to fetch sessions');
    return response.json();
  },

  createSession: async (data: { tutor: string; subject: string; payment: number }) => {
    const response = await fetch(`${API_BASE_URL}/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create session');
    return response.json();
  },

  completeSession: async (sessionId: number) => {
    const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/complete`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to complete session');
    return response.json();
  },

  // Quiz
  generateQuiz: async (data: { subject: string; difficulty?: string }): Promise<Quiz> => {
    const response = await fetch(`${API_BASE_URL}/quiz/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to generate quiz');
    return response.json();
  },
}; 