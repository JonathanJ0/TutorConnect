
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthForm from '@/components/AuthForm';
import { supabase } from '@/lib/supabase';
import { toast } from 'sonner';
import { SAMPLE_TUTORS, UserProfile } from '@/lib/types';

interface LoginProps {
  setUser: (user: UserProfile) => void;
}

const Login: React.FC<LoginProps> = ({ setUser }) => {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleLogin = async (data: any) => {
    setIsSubmitting(true);
    
    try {
      const { email, password } = data;
      
      // Mock sign in with Supabase
      const { data: authData, error } = await supabase.auth.signIn({
        email,
        password,
      });
      
      if (error) {
        throw error;
      }
      
      // Check if user already exists in localStorage
      const storedUser = localStorage.getItem('tutorapp_user');
      
      if (storedUser) {
        // User exists, load their profile
        const user = JSON.parse(storedUser);
        setUser(user);
      } else {
        // For demo, create a sample user
        // In a real app, we would fetch the user profile from Supabase
        const sampleTutor = SAMPLE_TUTORS.find(t => t.email === email);
        
        if (sampleTutor) {
          // Use sample tutor
          localStorage.setItem('tutorapp_user', JSON.stringify(sampleTutor));
          setUser(sampleTutor);
        } else {
          // Create default learner profile
          const newUser: UserProfile = {
            id: 'demo-user',
            email,
            role: 'learner',
            subjects: [],
            availability: [],
            created_at: new Date().toISOString(),
          };
          
          localStorage.setItem('tutorapp_user', JSON.stringify(newUser));
          setUser(newUser);
        }
      }
      
      // Show success message
      toast.success('Signed in successfully!');
      
      // Redirect to profile
      navigate('/profile');
    } catch (error: any) {
      console.error('Login error:', error);
      
      // For demo purposes, create a default user anyway
      const newUser: UserProfile = {
        id: 'demo-user',
        email: data.email,
        role: 'learner',
        subjects: [],
        availability: [],
        created_at: new Date().toISOString(),
      };
      
      localStorage.setItem('tutorapp_user', JSON.stringify(newUser));
      setUser(newUser);
      
      toast.success('Signed in with demo account!');
      navigate('/profile');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="page-container max-w-md mx-auto mt-8">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Welcome back</h1>
        <p className="text-gray-600">
          Sign in to your TutorConnect account
        </p>
      </div>
      
      <div className="bg-white p-6 sm:p-8 rounded-xl shadow-card border border-gray-100">
        <AuthForm type="login" onSubmit={handleLogin} />
        
        <div className="mt-6 text-center text-sm">
          <p className="text-gray-600">
            Don't have an account?{' '}
            <Link to="/register" className="text-tutorblue-600 hover:text-tutorblue-700 font-medium">
              Sign up
            </Link>
          </p>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200">
          <p className="text-xs text-center text-gray-500 mb-4">
            For demo purposes, you can sign in with any email and password. 
            Try using sample emails like john.doe@example.com or create your own account.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
