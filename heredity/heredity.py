import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])


    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)
            
    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    probability = 0
    joint_probability = 1

    for person in people:
        if person in one_gene: gene_number = 1
        elif person in two_genes: gene_number = 2
        else: gene_number = 0

        if person in have_trait: trait = True
        else: trait = False

        #do they have parents?
        if (people[person]['mother'] == None) and (people[person]['father'] == None):
            probability = PROBS['trait'][gene_number][trait] * PROBS['gene'][gene_number]

        else: #CONDITIONAL PROBABILITY (HAS PARENTS) & MUTATIONS 
            #find both parents number of genes
            mom_genes = -1
            dad_genes = -1

            if people[person]['mother'] in one_gene: mom_genes = 1
            elif people[person]['mother'] in two_genes: mom_genes = 2
            else: mom_genes = 0

            if people[person]['father'] in one_gene: dad_genes = 1
            elif people[person]['father'] in two_genes: dad_genes = 2
            else: dad_genes = 0

            #base probabilities:
            event_one = 0
            event_two = 0

            # 1) dad had zero genes P(don't) = 99%   
            if(dad_genes == 0): 
                event_one = 0.99
            # 2) dad had 1 gene P(don't) = 50%  (equal chance mutate both ways so it is equal) 
            elif(dad_genes == 1):
                event_one = 0.5
            # 3) dad had 2 P(don't) = 1% mutation 
            else:
                event_one = 0.01

            #opposite probabilities of dad for mom:
            if(mom_genes == 0):
                event_two = 0.01
            elif(mom_genes == 1):
                event_two = 0.5
            else:
                event_two = 0.99      

            #TRAIT CHANCE
            trait_chance = 0
            trait_chance = PROBS["trait"][gene_number][trait]
            

            #find probability based on parent combination
            if person in one_gene: 
                probability = ((event_one * event_two) + ((1-event_one) * (1-event_two))) * trait_chance #last part represents the OPPOSITE events happening since P(A) + P(Not A) = 1
            elif person in two_genes: 
                #dad did & mom did
                probability = (1-event_one) * event_two * trait_chance
            else: 
                #both didn't
                probability = (event_one) * (1-event_two) * trait_chance

        
        joint_probability *= probability
        probability = 0

    return joint_probability



def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    for person in probabilities:
        if person in two_genes:
            person_gene = 2

        elif person in one_gene:
            person_gene = 1
        else:
            person_gene = 0

        trait = False
        if person in have_trait:
            trait = True
            
        probabilities[person]['gene'][person_gene] += p
        probabilities[person]['trait'][trait] += p 

    return probabilities



def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        x = probabilities[person]['trait'][True]
        y = probabilities[person]['trait'][False]

        k = 1/(x + y)
        probabilities[person]['trait'][True] = k*x
        probabilities[person]['trait'][False] = k*y

        a = probabilities[person]['gene'][2]
        b = probabilities[person]['gene'][1]
        c = probabilities[person]['gene'][0]
        
        k = 1/(a+b+c)
        probabilities[person]['gene'][2] = k*a
        probabilities[person]['gene'][1] = k*b 
        probabilities[person]['gene'][0] = k*c


if __name__ == "__main__":
    main()
