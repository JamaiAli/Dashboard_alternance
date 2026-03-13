export type ApplicationStatus = 'Wishlist' | 'Applied' | 'Interview' | 'Technical Test' | 'Rejected' | 'Offer';

export const COLUMNS: { id: ApplicationStatus; title: string }[] = [
    { id: 'Wishlist', title: 'WISHLIST' },
    { id: 'Applied', title: 'APPLIED' },
    { id: 'Interview', title: 'INTERVIEW' },
    { id: 'Technical Test', title: 'TECH TEST' },
    { id: 'Offer', title: 'OFFER' },
    { id: 'Rejected', title: 'REJECTED' },
];

export type ApplicationType = 'Alternance' | 'Stage';

export interface Application {
    id: string;
    company_id: string;
    date_sent: string | null;
    last_contact_date: string;
    status: ApplicationStatus;
    salary_proposed: number | null;
    type: ApplicationType;
    job_url: string | null;
    raw_description: string | null;
    company?: {
        id: string;
        name: string;
        sector: string | null;
        tech_stack?: string[];
    };
}
