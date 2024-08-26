import React from 'react';
import { TreasureMap, Shield, Swords, Bell } from 'lucide-react';

const FeatureCard = ({ icon, title, description, color }) => (
  <div className={`bg-${color}-100 p-4 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300`}>
    <div className={`text-${color}-600 mb-2`}>{icon}</div>
    <h3 className={`text-${color}-800 font-bold mb-2`}>{title}</h3>
    <p className={`text-${color}-700 text-sm`}>{description}</p>
  </div>
);

const Slide = () => (
  <div className="bg-gradient-to-br from-purple-100 to-blue-100 p-6 rounded-lg shadow-xl">
    <h1 className="text-3xl font-bold mb-6 text-center text-purple-800">Unlock the Magic of SpendiFy!</h1>
    
    <div className="grid grid-cols-2 gap-4">
      <FeatureCard 
        icon={<TreasureMap size={32} />}
        title="Point Pirate's Paradise"
        description="Ahoy, matey! Transform every purchase into a treasure hunt. SpendiFy helps you plunder points and unearth hidden rewards. X marks the spot for savings!"
        color="yellow"
      />
      
      <FeatureCard 
        icon={<Shield size={32} />}
        title="Financial Force Field"
        description="Activate your financial force field! SpendiFy's insurance recommendations are like a superhero cape for your wallet. Zap away worries and power up your peace of mind!"
        color="green"
      />
      
      <FeatureCard 
        icon={<Swords size={32} />}
        title="Negotiation Dojo"
        description="Unleash your inner deal-making dragon! Arm yourself with SpendiFy's data and breathe fire in bank negotiations. Slash rates and score epic perks like a true financial ninja!"
        color="red"
      />
      
      <FeatureCard 
        icon={<Bell size={32} />}
        title="Reward Radar"
        description="Activate your SpendiFy sonar! Detect deals from miles away and never let a juicy offer swim by. Dive into a sea of savings with notifications that make a splash in your wallet!"
        color="blue"
      />
    </div>
    
    <p className="text-center mt-6 text-purple-800 font-semibold text-lg">
      Ready to embark on your financial adventure? SpendiFy: Where every swipe tells a story!
    </p>
  </div>
);

export default Slide;