import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  questions: [],
  answers: {},
  currentQuestionIndex: 0,
  completedQuestions: [], // Array of question indices that are completed
  formMetadata: {
    startedAt: null,
    lastUpdatedAt: null,
    estimatedTotalTime: '',
    estimatedTotalCost: '',
  }
};

const formSlice = createSlice({
  name: 'form',
  initialState,
  reducers: {
    setQuestions: (state, action) => {
      state.questions = action.payload;
      state.formMetadata.startedAt = new Date().toISOString();
    },
    
    setAnswer: (state, action) => {
      const { questionId, value } = action.payload;
      state.answers[questionId] = value;
      state.formMetadata.lastUpdatedAt = new Date().toISOString();
    },
    
    setCurrentQuestionIndex: (state, action) => {
      state.currentQuestionIndex = action.payload;
    },
    
    markQuestionComplete: (state, action) => {
      const questionIndex = action.payload;
      if (!state.completedQuestions.includes(questionIndex)) {
        state.completedQuestions.push(questionIndex);
      }
    },
    
    markQuestionIncomplete: (state, action) => {
      const questionIndex = action.payload;
      state.completedQuestions = state.completedQuestions.filter(
        index => index !== questionIndex
      );
    },
    
    setFormMetadata: (state, action) => {
      state.formMetadata = {
        ...state.formMetadata,
        ...action.payload
      };
    },
    
    goToQuestion: (state, action) => {
      state.currentQuestionIndex = action.payload;
    },
    
    nextQuestion: (state) => {
      if (state.currentQuestionIndex < state.questions.length - 1) {
        state.currentQuestionIndex += 1;
      }
    },
    
    previousQuestion: (state) => {
      if (state.currentQuestionIndex > 0) {
        state.currentQuestionIndex -= 1;
      }
    },
    
    resetForm: (state) => {
      return initialState;
    }
  }
});

export const {
  setQuestions,
  setAnswer,
  setCurrentQuestionIndex,
  markQuestionComplete,
  markQuestionIncomplete,
  setFormMetadata,
  goToQuestion,
  nextQuestion,
  previousQuestion,
  resetForm
} = formSlice.actions;

export default formSlice.reducer;

