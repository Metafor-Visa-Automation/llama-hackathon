import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  application: null,
  // Structure:
  // {
  //   app_id: string,
  //   user_id: string,
  //   application_name: string,
  //   country_code: string,
  //   travel_purpose: string,
  //   application_start_date: ISO string,
  //   application_end_date: ISO string,
  //   status: string,
  //   application_steps: [
  //     {
  //       step_id: string,
  //       title: string,
  //       description: string,
  //       priority_score: number,
  //       requires_document: boolean,
  //       source_urls: array,
  //       completed: boolean  // Initially false
  //     }
  //   ],
  //   created_at: ISO string,
  //   updated_at: ISO string
  // }
};

const applicationSlice = createSlice({
  name: 'application',
  initialState,
  reducers: {
    createApplication: (state, action) => {
      const { 
        mockResponseData, 
        user, 
        destinationCountry, 
        startDate, 
        endDate, 
        applicationType 
      } = action.payload;

      // Map action_steps to application_steps with completed field
      const applicationSteps = mockResponseData.action_steps.map(step => ({
        step_id: step.step_id,
        title: step.title,
        description: step.description,
        priority_score: step.priority_score,
        requires_document: step.requires_document,
        source_urls: step.source_urls,
        completed: false, // Initially false
        // Include all other fields from the step
        category: step.category,
        mandatory: step.mandatory,
        estimated_duration: step.estimated_duration,
        cost_estimate: step.cost_estimate,
        detailed_instructions: step.detailed_instructions,
        common_mistakes: step.common_mistakes,
        helpful_tips: step.helpful_tips,
      }));

      const now = new Date().toISOString();

      state.application = {
        app_id: `app_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`, // Generate unique ID
        user_id: user?.id || user?.user_id || '',
        application_name: `${destinationCountry?.name || 'Visa'} Application`,
        country_code: destinationCountry?.code || '',
        travel_purpose: mockResponseData.travel_purpose || '',
        application_start_date: startDate,
        application_end_date: endDate,
        application_type: applicationType,
        status: 'in_progress',
        application_steps: applicationSteps,
        created_at: now,
        updated_at: now,
      };

      console.log('📝 Application Created:', state.application);
    },

    updateApplicationStep: (state, action) => {
      const { stepId, completed } = action.payload;

      if (state.application && state.application.application_steps) {
        const step = state.application.application_steps.find(s => s.step_id === stepId);
        if (step) {
          step.completed = completed;
          state.application.updated_at = new Date().toISOString();
          console.log(`✏️ Application Step Updated - Step ID: ${stepId}, Completed: ${completed}`);
          console.log('Current Application State:', state.application);
        }
      }
    },

    completeApplicationStep: (state, action) => {
      const stepId = action.payload;

      if (state.application && state.application.application_steps) {
        const step = state.application.application_steps.find(s => s.step_id === stepId);
        if (step) {
          step.completed = true;
          state.application.updated_at = new Date().toISOString();
          console.log(`✅ Step Completed - Step ID: ${stepId}, Title: ${step.title}`);
          console.log('Current Application State:', state.application);
        }
      }
    },

    incompleteApplicationStep: (state, action) => {
      const stepId = action.payload;

      if (state.application && state.application.application_steps) {
        const step = state.application.application_steps.find(s => s.step_id === stepId);
        if (step) {
          step.completed = false;
          state.application.updated_at = new Date().toISOString();
          console.log(`❌ Step Marked Incomplete - Step ID: ${stepId}, Title: ${step.title}`);
          console.log('Current Application State:', state.application);
        }
      }
    },

    updateApplicationStatus: (state, action) => {
      if (state.application) {
        state.application.status = action.payload;
        state.application.updated_at = new Date().toISOString();

        // If status is 'completed', set end date
        if (action.payload === 'completed') {
          state.application.application_end_date = new Date().toISOString();
        }

        console.log(`🔄 Application Status Updated: ${action.payload}`);
        console.log('Current Application State:', state.application);
      }
    },

    updateApplication: (state, action) => {
      if (state.application) {
        state.application = {
          ...state.application,
          ...action.payload,
          updated_at: new Date().toISOString(),
        };

        console.log('🔧 Application Updated with:', action.payload);
        console.log('Current Application State:', state.application);
      }
    },

    resetApplication: (state) => {
      console.log('🗑️ Application Reset');
      state.application = null;
    }
  }
});

export const {
  createApplication,
  updateApplicationStep,
  completeApplicationStep,
  incompleteApplicationStep,
  updateApplicationStatus,
  updateApplication,
  resetApplication
} = applicationSlice.actions;

export default applicationSlice.reducer;
